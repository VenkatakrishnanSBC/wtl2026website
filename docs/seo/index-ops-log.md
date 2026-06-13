# WTL — Search Growth Ops Log

Loop: MEASURE → RESEARCH → DIAGNOSE → FIX one thing → VERIFY → LOG.
Site: worldtransgroup.com (Express/EJS, trilingual EN//fr//de). Mission: **Reliability & local mastery** — "the West Africa logistics partner who actually delivers" (Port of Dakar / ECOWAS customs depth, 25 years).

Auth note: SA-key flow does NOT work here (SA was never granted access to the GSC/GA4 properties; that grant was rejected). Measurement uses an **OAuth Playground access token** (scopes `analytics.readonly` + `webmasters.readonly`) pasted into `tools/seo-export/.env` → `python -m seo_export export-all`. Tokens expire ~1h. GA4 property `522906701`, GSC `sc-domain:worldtransgroup.com`.

---

## 2026-06-05 — cycle 1
| indexed | unknown | crawled-not-idx | impressions 28d | clicks 28d | organic sessions 28d | key events |
|---|---|---|---|---|---|---|
| n/a* | n/a* | n/a* | 1108 | 21 | 156 | 42 |

\*URL Inspection bucketing not pulled this cycle (OAuth token expired; no live GSC). Figures are from the 2026-06-04 `export-all` baseline (`tools/seo-export/exports/2026-06-04/`).

**Diagnosis (named blocker): DEPLOY-PATH DESYNC — shipped fixes are invisible to Google.**
Production is served by Firebase Cloud Function `app` sourced from `functions/`, a hand-maintained *duplicate* of the root app with **no build/sync step**. The prior two commits (SEO de-cannibalization + new content) edited only the root copy, so production (curled live) still served the OLD titles, the two new blog posts 404'd, and the sitemap fix was absent. This masks every downstream SEO layer (indexation, CTR, rankings) — no content fix counts until it's both synced into `functions/` AND deployed.

**Research delta (refresh from 2026-06-04 GSC queries):**
- Money query **"freight forwarding senegal"** = 262 impr split across `/`, `/contact`, `/about/overview`, **0 clicks** → consolidated to `/services/forwarding` last session.
- **Breakbulk cluster** ("breakbulk cargo/services/freight forwarder to senegal") ~97 impr, pos 11–15, 0 clicks → high-margin, now targeted on `/services/freight` + new BESC/port guides.
- Branded zero-CTR: "wtl logistics" (43+22+12 impr, 0 clicks), "world trans group" converts (11 clicks). FR: "stockage marchandises dakar" pos 10.5 (page-1 within reach). DE pages near-orphan (terms page ranking for "seefrachtransport").
- Sibling sites in same GSC account (potential internal-network linking / comparison): netlogisticsenegal.com, effitrans, africabuildings, sbcgrow. Full competitor teardown still TODO (deferred — blocker this cycle was not keyword targeting).
- keyword-map.md created with current targeting status.

**Fix shipped:** Synced 12 changed files (locales ×3, blog data, routes ×2, views ×5, sitemap) root→`functions/`; verified the `functions/` app boots and serves new titles, breakbulk section, ItemList schema, and new posts. Commit `d64f00a`. (Prior session: `24339bd` SEO fixes, `aec2454` export pipeline.)

**DEPLOYED 2026-06-05** ✅ `firebase deploy --only functions,hosting --project wtl2026website`. Verified live on production: new titles (`/services/forwarding`, `/services/freight`, `/about/values`, `/about/team`, `/fr/services/warehousing`), breakbulk section, founder Person schema (`Mamadou Sall`), both new guides 200 in EN/FR/DE, sitemap = 114 URLs with broken incoterms slug gone (0) and new posts present. Note: the CLI reported `functions[app] Skipped (No changes detected)` yet dynamic content updated old→new — don't trust that message; always curl-verify after deploy.

**Human actions pending (UI-only, no API):**
1. GSC → **URL Inspection → Request indexing** for the 5 retitled pages (`/services/forwarding`, `/services/freight`, `/about/team`, `/about/values`, `/about/overview`) and the 2 new guides — speeds snippet/title refresh.
2. Sitemap resubmit attempted programmatically this cycle (see below); confirm "Success" status in GSC → Sitemaps.
3. **Permanent deploy-path fix:** make `functions/` a build artifact (sync script + `predeploy` hook in firebase.json) or collapse to one source of truth. Until then **every future root edit must be mirrored into `functions/`.** Also: Node 20 runtime deprecated (decommission 2026-10-30) and firebase-functions is outdated — upgrade before October.

**Next cycle:** Get a fresh OAuth token, run `export-all`, pull URL-Inspection buckets for a real indexation count (baseline established: 1108 impr / 21 clicks / 156 sessions / 42 events). Measure CTR/position movement on the now-deployed targeted queries vs this baseline (~4–6 weeks for recrawl). Run the deferred competitor teardown. Enrich `/services/project-cargo` (breakbulk cluster) and decide invest-vs-deprioritize on DE service pages.
