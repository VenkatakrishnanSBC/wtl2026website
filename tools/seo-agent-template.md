# SEO Agent Template for Next.js Websites

> A comprehensive SEO audit and fix workflow for multilingual Next.js websites.
> Use this template with Claude Code or any AI assistant.

---

## Quick Start Prompt

Copy and paste this prompt to start an SEO audit:

```
I need you to perform a complete SEO audit and optimization for my Next.js website.

Website: [YOUR_DOMAIN]
Project Path: [YOUR_PROJECT_PATH]
Locales: [en, fr, de, ar] (adjust as needed)
Google Account: [YOUR_EMAIL]

Please execute the full SEO workflow:
1. Technical SEO audit (canonical, hreflang, redirects, sitemap)
2. Google Search Console analysis (if CLI access available)
3. GA4 traffic analysis (if CLI access available)
4. Fix all issues found
5. Submit to search engines (IndexNow + Google)
6. Generate status report

I have gcloud CLI authenticated and Firebase CLI ready.
```

---

## Full SEO Agent Workflow

### Phase 1: Technical SEO Audit

#### 1.1 Check Canonical Tags

```bash
# Check homepage canonical for each locale
for locale in en fr de ar; do
  echo "=== /$locale ==="
  curl -s "https://[DOMAIN]/$locale" | python3 -c "
import sys,re
html=sys.stdin.read()
canonical = re.findall(r'<link[^>]*rel=\"canonical\"[^>]*href=\"([^\"]+)\"', html)
print(f'Canonical: {canonical[0] if canonical else \"MISSING\"}')"
done
```

#### 1.2 Check Hreflang Tags

```bash
curl -s "https://[DOMAIN]/en" | python3 -c "
import sys,re
html=sys.stdin.read()
hreflangs = re.findall(r'hreflang=\"([^\"]+)\"[^>]*href=\"([^\"]+)\"', html)
for lang, url in hreflangs:
    print(f'{lang}: {url}')"
```

#### 1.3 Verify Sitemap

```bash
curl -s "https://[DOMAIN]/sitemap.xml" | head -100
```

#### 1.4 Check robots.txt

```bash
curl -s "https://[DOMAIN]/robots.txt"
```

---

### Phase 2: Google Search Console Analysis

#### 2.1 Authenticate gcloud with Required Scopes

```bash
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform,openid,https://www.googleapis.com/auth/userinfo.email"
```

#### 2.2 List Search Console Properties

```bash
TOKEN=$(gcloud auth application-default print-access-token)
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: [GCP_PROJECT_ID]" \
  "https://www.googleapis.com/webmasters/v3/sites"
```

#### 2.3 Get Search Performance (Last 90 Days)

```bash
TOKEN=$(gcloud auth application-default print-access-token)

# By date
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: [GCP_PROJECT_ID]" \
  -H "Content-Type: application/json" \
  "https://searchconsole.googleapis.com/webmasters/v3/sites/sc-domain%3A[DOMAIN]/searchAnalytics/query" \
  -d '{
    "startDate": "[90_DAYS_AGO]",
    "endDate": "[TODAY]",
    "dimensions": ["date"],
    "rowLimit": 100
  }'

# By query
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: [GCP_PROJECT_ID]" \
  -H "Content-Type: application/json" \
  "https://searchconsole.googleapis.com/webmasters/v3/sites/sc-domain%3A[DOMAIN]/searchAnalytics/query" \
  -d '{
    "startDate": "[90_DAYS_AGO]",
    "endDate": "[TODAY]",
    "dimensions": ["query"],
    "rowLimit": 25
  }'

# By page
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: [GCP_PROJECT_ID]" \
  -H "Content-Type: application/json" \
  "https://searchconsole.googleapis.com/webmasters/v3/sites/sc-domain%3A[DOMAIN]/searchAnalytics/query" \
  -d '{
    "startDate": "[90_DAYS_AGO]",
    "endDate": "[TODAY]",
    "dimensions": ["page"],
    "rowLimit": 25
  }'

# By country
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: [GCP_PROJECT_ID]" \
  -H "Content-Type: application/json" \
  "https://searchconsole.googleapis.com/webmasters/v3/sites/sc-domain%3A[DOMAIN]/searchAnalytics/query" \
  -d '{
    "startDate": "[90_DAYS_AGO]",
    "endDate": "[TODAY]",
    "dimensions": ["country"],
    "rowLimit": 15
  }'
```

#### 2.4 Check Sitemap Status

```bash
TOKEN=$(gcloud auth application-default print-access-token)
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: [GCP_PROJECT_ID]" \
  "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3A[DOMAIN]/sitemaps"
```

#### 2.5 URL Inspection (Check Indexing Status)

```bash
TOKEN=$(gcloud auth application-default print-access-token)

for url in \
  "https://[DOMAIN]/en" \
  "https://[DOMAIN]/fr" \
  "https://[DOMAIN]/en/contact" \
  "https://[DOMAIN]/en/services/[SERVICE_PAGE]"; do
  echo "=== $url ==="
  curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "x-goog-user-project: [GCP_PROJECT_ID]" \
    -H "Content-Type: application/json" \
    "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect" \
    -d "{\"inspectionUrl\": \"$url\", \"siteUrl\": \"sc-domain:[DOMAIN]\"}" | \
    python3 -c "
import sys,json
d=json.load(sys.stdin)
r=d['inspectionResult']['indexStatusResult']
print(f\"  Status: {r['verdict']}\")
print(f\"  Coverage: {r['coverageState']}\")
print(f\"  Canonical: {r.get('googleCanonical','N/A')}\")
print(f\"  Last crawl: {r.get('lastCrawlTime','N/A')}\")"
done
```

---

### Phase 3: GA4 Analysis

#### 3.1 List GA4 Properties

```bash
TOKEN=$(gcloud auth application-default print-access-token)
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: [GCP_PROJECT_ID]" \
  "https://analyticsadmin.googleapis.com/v1beta/accountSummaries"
```

#### 3.2 Traffic by Channel

```bash
TOKEN=$(gcloud auth application-default print-access-token)
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: [GCP_PROJECT_ID]" \
  -H "Content-Type: application/json" \
  "https://analyticsdata.googleapis.com/v1beta/properties/[GA4_PROPERTY_ID]:runReport" \
  -d '{
    "dateRanges": [{"startDate": "[90_DAYS_AGO]", "endDate": "[TODAY]"}],
    "dimensions": [{"name": "sessionDefaultChannelGroup"}],
    "metrics": [
      {"name": "activeUsers"},
      {"name": "sessions"},
      {"name": "screenPageViews"},
      {"name": "bounceRate"}
    ],
    "orderBys": [{"metric": {"metricName": "sessions"}, "desc": true}],
    "limit": 20
  }'
```

#### 3.3 Traffic by Country

```bash
TOKEN=$(gcloud auth application-default print-access-token)
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: [GCP_PROJECT_ID]" \
  -H "Content-Type: application/json" \
  "https://analyticsdata.googleapis.com/v1beta/properties/[GA4_PROPERTY_ID]:runReport" \
  -d '{
    "dateRanges": [{"startDate": "[90_DAYS_AGO]", "endDate": "[TODAY]"}],
    "dimensions": [{"name": "country"}],
    "metrics": [{"name": "activeUsers"}, {"name": "sessions"}],
    "orderBys": [{"metric": {"metricName": "sessions"}, "desc": true}],
    "limit": 15
  }'
```

#### 3.4 Top Pages

```bash
TOKEN=$(gcloud auth application-default print-access-token)
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: [GCP_PROJECT_ID]" \
  -H "Content-Type: application/json" \
  "https://analyticsdata.googleapis.com/v1beta/properties/[GA4_PROPERTY_ID]:runReport" \
  -d '{
    "dateRanges": [{"startDate": "[90_DAYS_AGO]", "endDate": "[TODAY]"}],
    "dimensions": [{"name": "pagePath"}],
    "metrics": [
      {"name": "screenPageViews"},
      {"name": "activeUsers"},
      {"name": "bounceRate"}
    ],
    "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": true}],
    "limit": 20
  }'
```

#### 3.5 Device Breakdown

```bash
TOKEN=$(gcloud auth application-default print-access-token)
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-goog-user-project: [GCP_PROJECT_ID]" \
  -H "Content-Type: application/json" \
  "https://analyticsdata.googleapis.com/v1beta/properties/[GA4_PROPERTY_ID]:runReport" \
  -d '{
    "dateRanges": [{"startDate": "[90_DAYS_AGO]", "endDate": "[TODAY]"}],
    "dimensions": [{"name": "deviceCategory"}],
    "metrics": [
      {"name": "activeUsers"},
      {"name": "sessions"},
      {"name": "bounceRate"},
      {"name": "averageSessionDuration"}
    ],
    "limit": 10
  }'
```

---

### Phase 4: Common SEO Fixes

#### 4.1 Create lib/seo.ts Helper

```typescript
// lib/seo.ts
import { locales } from '@/i18n/config';

const BASE_URL = 'https://[DOMAIN]';

/**
 * Generate canonical URL and hreflang alternates for a given locale and path.
 * Use in every page's generateMetadata to fix duplicate content issues.
 */
export function getAlternates(locale: string, path: string = '') {
  const cleanPath = path ? `/${path}` : '';
  const languages: Record<string, string> = {};

  for (const loc of locales) {
    languages[loc] = `${BASE_URL}/${loc}${cleanPath}`;
  }
  languages['x-default'] = `${BASE_URL}/en${cleanPath}`;

  return {
    canonical: `${BASE_URL}/${locale}${cleanPath}`,
    languages,
  };
}
```

#### 4.2 Add generateMetadata to Every Page

```typescript
// app/[locale]/page.tsx (and all other pages)
import type { Metadata } from "next";
import { getTranslations } from 'next-intl/server';
import { getAlternates } from "@/lib/seo";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'Metadata' });
  return {
    title: t('pageTitle'),
    description: t('pageDescription'),
    alternates: getAlternates(locale, 'page-path'), // e.g., 'services/ai-bpa'
  };
}
```

#### 4.3 Remove alternates from Root Layout

If you have `alternates` in `app/layout.tsx`, REMOVE it. Each page should set its own canonical via `generateMetadata`. Root layout alternates conflict with page-level metadata.

#### 4.4 Add 301 Redirects in next.config.js

```javascript
// next.config.js
module.exports = {
  async redirects() {
    return [
      // Old WordPress URLs to new pages
      { source: '/old-page/', destination: '/en/new-page', permanent: true },
      { source: '/old-page', destination: '/en/new-page', permanent: true },
      // Add all legacy URLs here
    ];
  },
};
```

#### 4.5 Ensure Trailing Slash Consistency

Pick either trailing slash or no trailing slash and be consistent. In `next.config.js`:

```javascript
module.exports = {
  trailingSlash: false, // or true - pick one
};
```

---

### Phase 5: Submit to Search Engines

#### 5.1 IndexNow (Bing, Yandex, DuckDuckGo, ChatGPT Search)

```bash
# Submit all URLs to IndexNow central API
INDEXNOW_KEY="[YOUR_INDEXNOW_KEY]"
DOMAIN="[YOUR_DOMAIN]"

# Build URL list from sitemap
URLS=$(curl -s "https://$DOMAIN/sitemap.xml" | grep -oP '(?<=<loc>)[^<]+' | jq -R -s -c 'split("\n") | map(select(length > 0))')

curl -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json" \
  -d "{
    \"host\": \"$DOMAIN\",
    \"key\": \"$INDEXNOW_KEY\",
    \"keyLocation\": \"https://$DOMAIN/$INDEXNOW_KEY.txt\",
    \"urlList\": $URLS
  }"
```

#### 5.2 Bing Direct Submission

```bash
INDEXNOW_KEY="[YOUR_INDEXNOW_KEY]"
for url in [LIST_OF_URLS]; do
  curl -s "https://www.bing.com/indexnow?url=$url&key=$INDEXNOW_KEY"
done
```

#### 5.3 Yandex Direct Submission

```bash
INDEXNOW_KEY="[YOUR_INDEXNOW_KEY]"
for url in [LIST_OF_URLS]; do
  curl -s "https://yandex.com/indexnow?url=$url&key=$INDEXNOW_KEY"
done
```

#### 5.4 Google (Manual)

Google doesn't have an API for requesting indexing. Users must:
1. Go to https://search.google.com/search-console/inspect?resource_id=sc-domain:[DOMAIN]
2. Paste each URL and click "Request Indexing"
3. Limited to ~10-12 requests per day

---

### Phase 6: IndexNow Setup (If Not Already Done)

#### 6.1 Create IndexNow Key File

```bash
# Create the key verification file
echo "[YOUR_INDEXNOW_KEY]" > public/[YOUR_INDEXNOW_KEY].txt
```

#### 6.2 Create IndexNow API Route

```typescript
// app/api/indexnow/route.ts
import { NextRequest, NextResponse } from 'next/server';

const INDEXNOW_KEY = process.env.INDEXNOW_KEY;
const SITE_URL = 'https://[DOMAIN]';

export async function POST(request: NextRequest) {
  try {
    const authKey = request.headers.get('x-api-key');
    if (!process.env.ADMIN_API_KEY || authKey !== process.env.ADMIN_API_KEY) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    if (!INDEXNOW_KEY) {
      return NextResponse.json({ error: 'INDEXNOW_KEY not configured' }, { status: 500 });
    }

    const { urls } = await request.json();

    if (!urls || !Array.isArray(urls) || urls.length === 0 || urls.length > 100) {
      return NextResponse.json({ error: 'URLs array is required (1-100 items)' }, { status: 400 });
    }

    const response = await fetch('https://api.indexnow.org/indexnow', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        host: '[DOMAIN]',
        key: INDEXNOW_KEY,
        keyLocation: `${SITE_URL}/${INDEXNOW_KEY}.txt`,
        urlList: urls.map((url: string) => `${SITE_URL}${url}`),
      }),
    });

    if (response.ok || response.status === 202) {
      return NextResponse.json({ success: true, submittedUrls: urls.length });
    }

    return NextResponse.json({ error: 'Failed to submit' }, { status: 500 });
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
```

#### 6.3 Add Environment Variables

```bash
# .env.local
INDEXNOW_KEY=your-unique-key-here
ADMIN_API_KEY=your-admin-key-here
```

---

## SEO Status Report Template

```markdown
## [WEBSITE] SEO Status Report — [DATE]

### Google Search Console (sc-domain:[DOMAIN])

**Sitemap:** X URLs submitted, Y indexed

**Indexing Status:**
| Page | Status | Last Crawled | Google Canonical |
|------|--------|-------------|-----------------|
| /en | Indexed/Not Indexed | DATE | URL |

**Search Performance (Last 90 Days):**
- Total impressions: X
- Total clicks: X
- Average CTR: X%
- Average position: X

**Top Queries:**
| Query | Impressions | Clicks | Position |
|-------|-------------|--------|----------|

**Impressions by Country:**
| Country | Impressions | Clicks |
|---------|-------------|--------|

### Google Analytics 4

**Overall:**
- Active users: X
- Sessions: X
- Page views: X
- Bounce rate: X%

**Traffic by Channel:**
| Channel | Sessions | Users | Bounce Rate |
|---------|----------|-------|-------------|

**Traffic by Country:**
| Country | Users | Sessions |
|---------|-------|----------|

**Top Pages:**
| Page | Views | Users | Bounce |
|------|-------|-------|--------|

### Issues Found
1. Issue description
2. Issue description

### Actions Taken
1. Action description
2. Action description

### Recommendations
1. Recommendation
2. Recommendation
```

---

## Checklist

### Technical SEO
- [ ] Every page has unique, locale-specific canonical URL
- [ ] Hreflang tags present for all locales + x-default
- [ ] No `alternates` in root layout (pages set their own)
- [ ] Sitemap.xml includes all pages with hreflang
- [ ] robots.txt allows crawling
- [ ] No trailing slash inconsistencies
- [ ] 301 redirects for all old/legacy URLs
- [ ] Meta descriptions translated per locale (not hardcoded English)

### Search Console
- [ ] Property verified (sc-domain preferred)
- [ ] Sitemap submitted
- [ ] No coverage errors
- [ ] Core Web Vitals passing
- [ ] Mobile usability passing

### Indexing
- [ ] IndexNow key file deployed
- [ ] All URLs submitted to IndexNow
- [ ] Priority pages manually requested in Google Search Console

### Analytics
- [ ] GA4 property connected
- [ ] Tracking code on all pages
- [ ] Goals/conversions configured
