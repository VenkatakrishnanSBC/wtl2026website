# seo-export — GA4 + Search Console data pipeline for worldtransgroup.com

Python CLI that exports **GA4 landing-page behavior** and **Google Search Console
search analytics** into normalized CSV/JSON, then **reconciles** them on URL path to
surface *"High-Visibility, Low-Connection"* anomalies — pages with strong search
visibility (above-median impressions) but weak post-click engagement
(engagement rate < 0.5 **or** average engagement time < 20s).

The output feeds the GSC-query-intent ↔ GA4-post-click-behavior reconciliation
analysis (Layer 1 of the SEO/UX strategy).

Self-contained: nothing here touches the Node/Express site in the parent repo.

## Setup

### 1. Google Cloud project & APIs

1. Create (or reuse) a project at <https://console.cloud.google.com>.
2. Enable two APIs (APIs & Services → Library):
   - **Google Analytics Data API**
   - **Google Search Console API**

### 2. Service account & key

1. IAM & Admin → Service Accounts → **Create service account** (e.g. `wtl-seo-export`).
   No project-level roles are needed — access is granted inside GA4/GSC.
2. Open the account → Keys → **Add key → JSON**. Save it as
   `tools/seo-export/credentials/wtl-seo-export.json` (the `credentials/` dir is
   gitignored — never commit keys).
3. Note the service-account **email** (`...@...iam.gserviceaccount.com`) — you grant
   it access in the next step.

### 3. Grant the service account read access

- **GA4**: Admin → Property → **Property Access Management** → “+” → paste the
  service-account email → role **Viewer**.
- **Search Console**: open the `worldtransgroup.com` property → Settings →
  **Users and permissions** → **Add user** → paste the email → permission
  **Full** (or Restricted).

### 4. Configure & install

```bash
cd tools/seo-export
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit .env
```

`.env` values:

| Variable | Value |
|---|---|
| `GA4_PROPERTY_ID` | **Numeric** property ID (GA4 Admin → Property Settings → Property ID). NOT the `G-QVG2LR3XV1` measurement id. |
| `GSC_SITE_URL` | `https://worldtransgroup.com/` (URL-prefix, trailing slash required) **or** `sc-domain:worldtransgroup.com` (domain property) — match Search Console exactly. |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to the service-account JSON key. |

### 5. Verify before pulling data

```bash
python -m seo_export verify
```

Confirms credentials load, the GA4 property is reachable, and the GSC site list
contains `GSC_SITE_URL`. Run this first — it diagnoses the two most common
failures (service account not added in GA4 / GSC) with exact remediation steps.

## Commands

All commands accept `--start/--end` (default: last 90 days ending yesterday),
`--format csv|json` (default csv), `--out DIR`, `--credentials PATH`, `--env-file PATH`.
Output lands in `exports/YYYY-MM-DD/`.

```bash
# GA4 landing-page engagement (organic only, paths collapsed for joining)
python -m seo_export ga4-landing-pages --channel organic --strip-query

# Which key events fire on which landing pages
python -m seo_export ga4-key-events --channel organic --strip-query

# GSC query x page — hunt high-impression / low-CTR anomalies
python -m seo_export gsc-queries --min-impressions 100 --low-ctr-below 0.02

# Optional country/device splits (ISO-3166-1-alpha-3)
python -m seo_export gsc-queries --country sen --device mobile

# GSC page-level aggregates
python -m seo_export gsc-pages --min-impressions 10

# The joined report (the main deliverable)
python -m seo_export reconcile --channel organic

# Everything in one dated output set
python -m seo_export export-all
```

## Reconcile output & anomaly logic

`reconcile.csv` columns:

| Column | Meaning |
|---|---|
| `page` | Normalized path (no protocol/domain/query; trailing slash stripped; `/fr/` & `/de/` prefixes preserved). |
| `language` | `en` / `fr` / `de`, derived from the path prefix. |
| `top_queries` | Top 5 GSC queries for the page by impressions, pipe-separated. |
| `gsc_impressions`, `gsc_clicks`, `gsc_ctr`, `gsc_avg_position` | GSC page aggregates (ctr is a 0–1 float). |
| `ga4_sessions`, `ga4_engagement_rate` | GA4 sessions and engaged/total ratio for the landing page. |
| `ga4_avg_engagement_time_sec` | Total user engagement duration ÷ sessions. |
| `ga4_key_events`, `ga4_key_event_rate` | Key-event completions and per-session rate. |
| `anomaly` | `True` when the page has **above-median GSC impressions** AND GA4 data AND (**engagement_rate < 0.5** OR **avg engagement time < 20s**). |

These are the "High-Visibility, Low-Connection" pages: search shows the page often,
users click, but the on-page experience fails to hold them — the prime candidates
for vision-alignment rewrites.

Notes:

- GSC and GA4 measure differently (search clicks vs. sessions, different
  attribution windows); treat joined rows as directional, not accounting-grade.
- GSC data uses `dataState: final` — the last ~2 days are excluded by Google.
- The join is a full outer join: pages can appear with GSC-only or GA4-only data.

## Reliability

- Exponential backoff with jitter on HTTP 429/5xx for both APIs (honors `Retry-After`).
- GSC 25,000-row cap handled via `startRow` pagination — full datasets, not samples.
- Permission errors (403) raise messages that include the exact service-account
  email to add and where to add it.

## Layout

```
seo_export/
  cli.py        # argparse subcommands, dispatch, error presentation
  config.py     # .env loading, validation, default date range
  auth.py       # service-account / ADC credential loading, scopes
  ga4.py        # GA4 Data API adapter (landing pages, key events)
  gsc.py        # Search Console adapter (queries, pages, site list)
  reconcile.py  # GSC<->GA4 join + anomaly flagging
  normalize.py  # URL path canonicalization, numeric coercion, median
  retry.py      # backoff/retry shared by both adapters
  output.py     # dated CSV/JSON writers
```
