# SEO Agent Prompt for Claude Code

Copy this prompt and use it with Claude Code for any Next.js website.

---

## Full SEO Audit Prompt

```
Perform a complete SEO audit and optimization for this Next.js website.

## Configuration
- Domain: [REPLACE_WITH_DOMAIN]
- GCP Project ID: [REPLACE_WITH_PROJECT_ID]
- GA4 Property ID: [REPLACE_WITH_GA4_PROPERTY_ID]
- Locales: en, fr, de, ar (adjust as needed)
- IndexNow Key: Check .env.local or set one

## Tasks

### 1. Technical SEO Audit
Check and fix:
- Canonical tags (each page must have locale-specific canonical)
- Hreflang tags (all locales + x-default)
- Remove any `alternates` from root layout (pages set their own)
- Sitemap.xml validation
- robots.txt validation
- Trailing slash consistency
- 301 redirects for legacy URLs

### 2. Google Search Console Analysis
Using gcloud CLI (authenticate if needed):
- List verified properties
- Get search performance (impressions, clicks, CTR, position)
- Get top queries and pages
- Check sitemap status
- URL inspection for key pages (check indexing status)

### 3. GA4 Analysis
Using gcloud CLI:
- Traffic by channel (organic vs direct vs referral)
- Traffic by country
- Top pages by views
- Device breakdown
- Bounce rate analysis

### 4. Fix Issues Found
- Create lib/seo.ts helper if missing
- Add generateMetadata to all pages
- Add proper alternates with getAlternates()
- Translate meta descriptions per locale
- Add 301 redirects in next.config.js

### 5. Submit to Search Engines
- IndexNow: Submit all sitemap URLs to Bing/Yandex
- Provide list of URLs for manual Google Search Console submission

### 6. Generate Report
Create a summary with:
- Current indexing status
- Search performance metrics
- Traffic analysis
- Issues found and fixed
- Recommendations

## Auth Commands (if needed)

```bash
# Authenticate gcloud with required scopes
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform,openid,https://www.googleapis.com/auth/userinfo.email"
```

## Expected Output
- Fixed code files
- IndexNow submissions completed
- Comprehensive status report
- Next steps for manual actions
```

---

## Quick IndexNow Submission Prompt

```
Submit all sitemap URLs to IndexNow for immediate indexing on Bing, Yandex, and DuckDuckGo.

Domain: [DOMAIN]
IndexNow Key: [KEY] (or check .env.local)

1. Fetch sitemap.xml and extract all URLs
2. Submit to IndexNow central API (api.indexnow.org)
3. Submit key pages directly to Bing and Yandex
4. Report success/failure for each
```

---

## Search Console Check Prompt

```
Check Google Search Console status for [DOMAIN].

GCP Project: [PROJECT_ID]

1. Get search performance for last 90 days
2. Show top queries and their positions
3. Show top pages by clicks
4. Check sitemap indexing status
5. Run URL inspection on homepage and key service pages
6. Identify any indexing issues
```

---

## GA4 Traffic Analysis Prompt

```
Analyze GA4 traffic for [DOMAIN].

GA4 Property ID: [PROPERTY_ID]
GCP Project: [PROJECT_ID]

Show:
1. Traffic by channel (organic, direct, referral, paid)
2. Traffic by country (top 15)
3. Top 20 pages by views
4. Device breakdown (desktop vs mobile)
5. Bounce rate by channel
6. Identify any concerning patterns
```

---

## Canonical/Hreflang Fix Prompt

```
Fix canonical and hreflang issues for this Next.js i18n website.

Locales: [en, fr, de, ar]
Domain: [DOMAIN]

1. Create lib/seo.ts with getAlternates() helper if missing
2. Add generateMetadata with alternates to every page
3. Remove any alternates from root layout.tsx
4. Verify each locale homepage has correct canonical
5. Test and confirm fixes
```

---

## Post-Deploy SEO Verification Prompt

```
Verify SEO implementation after deployment.

Domain: [DOMAIN]

1. Check canonical tag on each locale homepage
2. Verify hreflang tags are present
3. Validate sitemap.xml is accessible
4. Check robots.txt
5. Submit updated URLs to IndexNow
6. Confirm all pages return 200 status
```
