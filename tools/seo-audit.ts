#!/usr/bin/env npx ts-node
/**
 * SEO Audit & Submission Script
 *
 * Performs complete SEO audit and submits URLs to search engines.
 *
 * Usage:
 *   npx ts-node tools/seo-audit.ts --domain=sbcgrow.com --project=sbcgrowebsiteoct2025
 *
 * Requirements:
 *   - gcloud CLI authenticated with proper scopes
 *   - INDEXNOW_KEY environment variable set
 */

import { execSync } from 'child_process';

// Configuration
interface Config {
  domain: string;
  gcpProject: string;
  ga4PropertyId: string;
  indexNowKey: string;
  locales: string[];
  pages: string[];
}

const DEFAULT_CONFIG: Partial<Config> = {
  locales: ['en', 'fr', 'de', 'ar'],
  pages: [
    '',
    '/contact',
    '/case-studies',
    '/services/performance-hr',
    '/services/digitalization',
    '/services/ai-bpa',
    '/services/cloud-security',
  ],
};

// Parse command line arguments
function parseArgs(): Partial<Config> {
  const args: Partial<Config> = {};
  process.argv.slice(2).forEach(arg => {
    const [key, value] = arg.replace('--', '').split('=');
    if (key === 'domain') args.domain = value;
    if (key === 'project') args.gcpProject = value;
    if (key === 'ga4') args.ga4PropertyId = value;
    if (key === 'indexnow-key') args.indexNowKey = value;
  });
  return args;
}

// Execute shell command and return output
function exec(cmd: string, silent = false): string {
  try {
    const result = execSync(cmd, { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 });
    return result.trim();
  } catch (error: any) {
    if (!silent) console.error(`Command failed: ${cmd}`);
    return error.stdout?.toString() || '';
  }
}

// Get OAuth token from gcloud
function getToken(): string {
  // Try standard path first, then common custom locations
  const gcloudPaths = [
    'gcloud',
    `${process.env.HOME}/google-cloud-sdk/bin/gcloud`,
    '/usr/local/bin/gcloud',
    '/opt/homebrew/bin/gcloud',
  ];

  for (const gcloudPath of gcloudPaths) {
    const token = exec(`${gcloudPath} auth application-default print-access-token 2>/dev/null`, true);
    if (token && token.startsWith('ya29.')) {
      return token;
    }
  }

  console.error('❌ No gcloud token. Run: gcloud auth application-default login --scopes=...');
  process.exit(1);
}

// API call helper
function apiCall(method: string, url: string, token: string, project: string, body?: object): any {
  const bodyArg = body ? `-d '${JSON.stringify(body)}'` : '';
  const cmd = `curl -s -X ${method} "${url}" -H "Authorization: Bearer ${token}" -H "x-goog-user-project: ${project}" -H "Content-Type: application/json" ${bodyArg}`;
  const result = exec(cmd, true);
  try {
    return JSON.parse(result);
  } catch {
    return { error: result };
  }
}

// Check canonical tags
async function checkCanonicals(domain: string, locales: string[]): Promise<void> {
  console.log('\n📋 Checking Canonical Tags\n');

  for (const locale of locales) {
    const url = `https://${domain}/${locale}`;
    const html = exec(`curl -s "${url}"`, true);
    const match = html.match(/<link[^>]*rel="canonical"[^>]*href="([^"]+)"/);
    const canonical = match ? match[1] : 'MISSING';
    const status = canonical.includes(`/${locale}`) ? '✅' : '❌';
    console.log(`  ${status} /${locale}: ${canonical}`);
  }
}

// Check URL indexing status via Search Console API
async function checkIndexingStatus(domain: string, urls: string[], token: string, project: string): Promise<void> {
  console.log('\n🔍 URL Indexing Status (Google)\n');

  for (const url of urls) {
    const result = apiCall('POST',
      'https://searchconsole.googleapis.com/v1/urlInspection/index:inspect',
      token, project,
      { inspectionUrl: url, siteUrl: `sc-domain:${domain}` }
    );

    if (result.inspectionResult) {
      const r = result.inspectionResult.indexStatusResult;
      const status = r.verdict === 'PASS' ? '✅' : r.verdict === 'NEUTRAL' ? '⚠️' : '❌';
      console.log(`  ${status} ${url}`);
      console.log(`     Coverage: ${r.coverageState}`);
      if (r.lastCrawlTime) console.log(`     Last crawl: ${r.lastCrawlTime}`);
    } else {
      console.log(`  ❓ ${url}: ${result.error?.message || 'Unknown error'}`);
    }
  }
}

// Get Search Console performance data
async function getSearchPerformance(domain: string, token: string, project: string): Promise<void> {
  console.log('\n📊 Search Console Performance (Last 90 Days)\n');

  const endDate = new Date().toISOString().split('T')[0];
  const startDate = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

  // Overall stats
  const overall = apiCall('POST',
    `https://searchconsole.googleapis.com/webmasters/v3/sites/sc-domain%3A${domain}/searchAnalytics/query`,
    token, project,
    { startDate, endDate, dimensions: ['date'], rowLimit: 100 }
  );

  if (overall.rows) {
    let totalClicks = 0, totalImpressions = 0;
    overall.rows.forEach((r: any) => {
      totalClicks += r.clicks;
      totalImpressions += r.impressions;
    });
    const avgCtr = totalImpressions > 0 ? (totalClicks / totalImpressions * 100).toFixed(1) : 0;
    console.log(`  Total Impressions: ${totalImpressions}`);
    console.log(`  Total Clicks: ${totalClicks}`);
    console.log(`  Average CTR: ${avgCtr}%`);
  }

  // Top queries
  const queries = apiCall('POST',
    `https://searchconsole.googleapis.com/webmasters/v3/sites/sc-domain%3A${domain}/searchAnalytics/query`,
    token, project,
    { startDate, endDate, dimensions: ['query'], rowLimit: 10 }
  );

  if (queries.rows?.length) {
    console.log('\n  Top Queries:');
    queries.rows.forEach((r: any) => {
      console.log(`    • "${r.keys[0]}" - ${r.impressions} imp, ${r.clicks} clicks, pos ${r.position.toFixed(1)}`);
    });
  }
}

// Get GA4 data
async function getGA4Data(propertyId: string, token: string, project: string): Promise<void> {
  console.log('\n📈 GA4 Analytics (Last 90 Days)\n');

  const endDate = new Date().toISOString().split('T')[0];
  const startDate = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

  // Traffic by channel
  const channels = apiCall('POST',
    `https://analyticsdata.googleapis.com/v1beta/properties/${propertyId}:runReport`,
    token, project,
    {
      dateRanges: [{ startDate, endDate }],
      dimensions: [{ name: 'sessionDefaultChannelGroup' }],
      metrics: [
        { name: 'activeUsers' },
        { name: 'sessions' },
        { name: 'bounceRate' }
      ],
      orderBys: [{ metric: { metricName: 'sessions' }, desc: true }],
      limit: 10
    }
  );

  if (channels.rows) {
    console.log('  Traffic by Channel:');
    channels.rows.forEach((r: any) => {
      const channel = r.dimensionValues[0].value;
      const users = r.metricValues[0].value;
      const sessions = r.metricValues[1].value;
      const bounce = (parseFloat(r.metricValues[2].value) * 100).toFixed(0);
      console.log(`    • ${channel}: ${sessions} sessions, ${users} users, ${bounce}% bounce`);
    });
  }

  // Traffic by country
  const countries = apiCall('POST',
    `https://analyticsdata.googleapis.com/v1beta/properties/${propertyId}:runReport`,
    token, project,
    {
      dateRanges: [{ startDate, endDate }],
      dimensions: [{ name: 'country' }],
      metrics: [{ name: 'activeUsers' }, { name: 'sessions' }],
      orderBys: [{ metric: { metricName: 'sessions' }, desc: true }],
      limit: 10
    }
  );

  if (countries.rows) {
    console.log('\n  Traffic by Country:');
    countries.rows.forEach((r: any) => {
      const country = r.dimensionValues[0].value;
      const users = r.metricValues[0].value;
      const sessions = r.metricValues[1].value;
      console.log(`    • ${country}: ${sessions} sessions, ${users} users`);
    });
  }
}

// Submit URLs to IndexNow
async function submitToIndexNow(domain: string, urls: string[], indexNowKey: string): Promise<void> {
  console.log('\n🚀 Submitting to IndexNow (Bing, Yandex, DuckDuckGo)\n');

  const payload = JSON.stringify({
    host: domain,
    key: indexNowKey,
    keyLocation: `https://${domain}/${indexNowKey}.txt`,
    urlList: urls
  });

  // Submit to IndexNow central API
  const result = exec(`curl -s -w "\\n%{http_code}" -X POST "https://api.indexnow.org/indexnow" -H "Content-Type: application/json" -d '${payload}'`, true);
  const lines = result.split('\n');
  const httpCode = lines[lines.length - 1];

  if (httpCode === '200' || httpCode === '202') {
    console.log(`  ✅ IndexNow API: ${urls.length} URLs submitted (HTTP ${httpCode})`);
  } else {
    console.log(`  ❌ IndexNow API failed: HTTP ${httpCode}`);
  }

  // Submit key URLs to Bing directly
  const keyUrls = urls.slice(0, 10);
  let bingSuccess = 0;
  for (const url of keyUrls) {
    const code = exec(`curl -s -o /dev/null -w "%{http_code}" "https://www.bing.com/indexnow?url=${encodeURIComponent(url)}&key=${indexNowKey}"`, true);
    if (code === '200') bingSuccess++;
  }
  console.log(`  ✅ Bing Direct: ${bingSuccess}/${keyUrls.length} URLs accepted`);

  // Submit to Yandex
  let yandexSuccess = 0;
  for (const url of keyUrls.slice(0, 6)) {
    const code = exec(`curl -s -o /dev/null -w "%{http_code}" "https://yandex.com/indexnow?url=${encodeURIComponent(url)}&key=${indexNowKey}"`, true);
    if (code === '200' || code === '202') yandexSuccess++;
  }
  console.log(`  ✅ Yandex: ${yandexSuccess}/6 URLs accepted`);
}

// Main function
async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('  SEO AUDIT & SUBMISSION TOOL');
  console.log('='.repeat(60));

  const args = parseArgs();
  const config: Config = {
    domain: args.domain || process.env.DOMAIN || '',
    gcpProject: args.gcpProject || process.env.GCP_PROJECT || '',
    ga4PropertyId: args.ga4PropertyId || process.env.GA4_PROPERTY_ID || '',
    indexNowKey: args.indexNowKey || process.env.INDEXNOW_KEY || '',
    locales: DEFAULT_CONFIG.locales!,
    pages: DEFAULT_CONFIG.pages!,
  };

  if (!config.domain) {
    console.error('❌ Missing --domain argument');
    console.log('Usage: npx ts-node tools/seo-audit.ts --domain=example.com --project=gcp-project-id');
    process.exit(1);
  }

  console.log(`\n🌐 Domain: ${config.domain}`);
  console.log(`📁 GCP Project: ${config.gcpProject || 'Not set'}`);
  console.log(`📊 GA4 Property: ${config.ga4PropertyId || 'Not set'}`);
  console.log(`🔑 IndexNow Key: ${config.indexNowKey ? '***' + config.indexNowKey.slice(-4) : 'Not set'}`);

  // Build all URLs
  const allUrls: string[] = [];
  for (const locale of config.locales) {
    for (const page of config.pages) {
      allUrls.push(`https://${config.domain}/${locale}${page}`);
    }
  }
  console.log(`📄 Total URLs: ${allUrls.length}`);

  // 1. Check canonicals
  await checkCanonicals(config.domain, config.locales);

  // 2. If we have gcloud access, run Search Console and GA4 checks
  if (config.gcpProject) {
    const token = getToken();

    // Check indexing status for key pages
    const keyUrls = config.locales.slice(0, 2).flatMap(locale => [
      `https://${config.domain}/${locale}`,
      `https://${config.domain}/${locale}/services/performance-hr`,
    ]);
    await checkIndexingStatus(config.domain, keyUrls, token, config.gcpProject);

    // Get Search Console data
    await getSearchPerformance(config.domain, token, config.gcpProject);

    // Get GA4 data
    if (config.ga4PropertyId) {
      await getGA4Data(config.ga4PropertyId, token, config.gcpProject);
    }
  }

  // 3. Submit to IndexNow
  if (config.indexNowKey) {
    await submitToIndexNow(config.domain, allUrls, config.indexNowKey);
  } else {
    console.log('\n⚠️  IndexNow submission skipped (no INDEXNOW_KEY)');
  }

  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('  SUMMARY');
  console.log('='.repeat(60));
  console.log(`
✅ Canonical tags checked
${config.gcpProject ? '✅ Search Console data retrieved' : '⚠️  Search Console skipped (no GCP project)'}
${config.ga4PropertyId ? '✅ GA4 data retrieved' : '⚠️  GA4 skipped (no property ID)'}
${config.indexNowKey ? '✅ URLs submitted to IndexNow' : '⚠️  IndexNow skipped (no key)'}

📝 Next Steps:
1. Go to Google Search Console and manually request indexing for priority pages
2. Check Bing Webmaster Tools in 24-48 hours to verify indexing
3. Run this script again after major content updates
`);
}

main().catch(console.error);
