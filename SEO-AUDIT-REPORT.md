# SEO Audit Report — worldtransgroup.com

**Date:** February 8, 2026
**Domain:** worldtransgroup.com
**Platform:** Express.js + EJS on Firebase Hosting/Cloud Functions
**Languages:** English (default), French, German

---

## Executive Summary

Comprehensive on-page SEO optimization completed for World Trans & Logistics (WTL) website. All 35 pages across 3 languages received keyword-optimized title tags, meta descriptions, meta keywords, and structured data (JSON-LD). A total of 11 files were modified with 802 lines added and 244 removed. 90+ URLs submitted to search engines via IndexNow.

---

## 1. Changes Made

### 1.1 Title Tag Optimization (28 titles x 3 languages = 84 title tags)

**Before:** Titles used full company name, averaged 55-78 characters.
```
World Trans & Logistics — Global Freight & Logistics Solutions in West Africa (78 chars)
Ocean Freight Services — World Trans & Logistics (49 chars)
```

**After:** Titles use "WTL" brand shorthand + location keywords, all under 60 characters.
```
Freight Forwarding Senegal | WTL Logistics Dakar, West Africa (60 chars)
Ocean Freight Senegal - FCL & LCL | WTL Dakar (47 chars)
```

| Section | Pages | EN Example | FR Example | DE Example |
|---------|-------|-----------|-----------|-----------|
| Home | 1 | Freight Forwarding Senegal \| WTL Logistics Dakar, West Africa | Transitaire Dakar Senegal \| WTL Logistique Afrique Ouest | Spedition Senegal \| WTL Logistik Dakar, Westafrika |
| Services | 11 | Ocean Freight Senegal - FCL & LCL \| WTL Dakar | Fret Maritime Dakar - FCL & LCL \| WTL Senegal | Seefracht Dakar - FCL & LCL \| WTL Senegal |
| About | 7 | About WTL \| Logistics Company Dakar, Senegal | A Propos de WTL \| Logistique Dakar, Senegal | Uber WTL \| Logistikunternehmen Dakar, Senegal |
| Contact | 5 | Contact WTL \| Freight Forwarder Dakar, Senegal | Contactez WTL \| Transitaire Dakar, Senegal | Kontakt WTL \| Spediteur Dakar, Senegal |
| Industries | 4 | Industries Served \| WTL Logistics Senegal | Industries Servies \| WTL Logistique Senegal | Branchen \| WTL Logistik Senegal |
| Blog | 1 | Logistics Blog \| Freight Industry News - WTL | Blog Logistique \| Actualites Fret - WTL | Logistik-Blog \| Frachtnachrichten Westafrika - WTL |
| Quote | 1 | Free Freight Quote \| WTL Logistics Senegal | Devis Fret Gratuit \| WTL Logistique Senegal | Kostenloses Frachtangebot \| WTL Logistik Senegal |

### 1.2 Meta Keywords Added (29 keyword sets x 3 languages)

Every page now has a `<meta name="keywords">` tag with 8-12 location-specific keywords per page.

**Homepage keywords (EN):**
```
freight forwarding Senegal, logistics company Dakar, ocean freight West Africa,
air freight Senegal, supply chain solutions Africa, shipping company Dakar,
customs clearance Senegal, warehousing Dakar, international logistics West Africa,
cargo shipping Senegal
```

**Homepage keywords (FR):**
```
transitaire Senegal, entreprise logistique Dakar, fret maritime Afrique de l'Ouest,
fret aerien Senegal, solutions logistiques Afrique, compagnie maritime Dakar,
dedouanement Senegal, entreposage Dakar, logistique internationale Afrique de l'Ouest,
expedition de fret Senegal
```

### 1.3 JSON-LD Structured Data Added

| Page Type | Schemas Added | Before | After |
|-----------|--------------|--------|-------|
| Homepage | Organization + WebSite | Organization only | Organization + WebSite |
| Service pages (10) | Organization + Service + BreadcrumbList | Organization only | 3 schemas each |
| About pages (7) | Organization + BreadcrumbList | Organization only | 2 schemas each |
| Contact pages (5) | Organization + BreadcrumbList | Organization only | 2 schemas each |
| FAQ page | Organization + FAQPage + BreadcrumbList | Organization + FAQPage | 3 schemas |
| Industry pages (4) | Organization + BreadcrumbList | Organization only | 2 schemas each |
| Blog listing | Organization + BreadcrumbList | Organization only | 2 schemas |
| Blog posts (6) | Organization + BlogPosting + BreadcrumbList | Organization + BlogPosting | 3 schemas |
| Quote page | Organization + BreadcrumbList | Organization only | 2 schemas |

**Service schema example:**
```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "serviceType": "Ocean Freight Shipping",
  "provider": {
    "@type": "Organization",
    "name": "World Trans & Logistics",
    "url": "https://worldtransgroup.com"
  },
  "areaServed": [
    { "@type": "Place", "name": "Senegal" },
    { "@type": "Place", "name": "West Africa" }
  ]
}
```

**BreadcrumbList schema example:**
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://worldtransgroup.com/" },
    { "@type": "ListItem", "position": 2, "name": "Services", "item": "https://worldtransgroup.com/services" },
    { "@type": "ListItem", "position": 3, "name": "Ocean Freight", "item": "https://worldtransgroup.com/services/ocean-freight" }
  ]
}
```

### 1.4 Template Infrastructure Update

**views/partials/head.ejs:**
- Added meta keywords tag rendering
- Updated JSON-LD rendering to support arrays (multiple schemas per page)

---

## 2. Technical SEO Status

### 2.1 Existing Infrastructure (Already In Place)

| Feature | Status | Details |
|---------|--------|---------|
| Canonical URLs | OK | `<link rel="canonical">` on every page |
| Hreflang tags | OK | EN, FR, DE, x-default on all pages |
| Open Graph tags | OK | og:title, og:description, og:url, og:type, og:image |
| Twitter Cards | OK | twitter:card, twitter:title, twitter:description |
| Responsive design | OK | Viewport meta, CSS media queries |
| robots.txt | OK | Allows all crawlers, links sitemap |
| Sitemap | OK | 105 URLs with hreflang alternates |
| HTTPS | OK | Enforced via Firebase Hosting |
| IndexNow key | OK | Verified at /0e223f45ebc24c9fb30b0667ccd5e440.txt |

### 2.2 Search Engine Submission Status

| Channel | Status | URLs Submitted |
|---------|--------|---------------|
| IndexNow (Bing, Yandex, etc.) | Submitted (HTTP 200) | 99 URLs across EN/FR/DE |
| Google Search Console | Sitemap submitted (previous session) | 105 URLs in sitemap |
| Google sitemap ping | Deprecated endpoint (HTTP 404) | N/A |

### 2.3 Search Console Baseline (from previous session)

| Metric | Value |
|--------|-------|
| Total impressions (90 days) | 29 |
| Total clicks (90 days) | 0 |
| Indexed pages | 3 of 105 |
| Coverage errors | 0 |

---

## 3. Files Modified

| File | Changes |
|------|---------|
| `locales/en.json` | 29 keyword sets + 28 optimized title tags |
| `locales/fr.json` | 29 keyword sets + 28 optimized title tags |
| `locales/de.json` | 29 keyword sets + 28 optimized title tags |
| `routes/services.js` | Service JSON-LD + BreadcrumbList + keywords (11 routes) |
| `routes/about.js` | BreadcrumbList + keywords (7 routes) |
| `routes/contact.js` | BreadcrumbList + keywords (6 routes) |
| `routes/industries.js` | BreadcrumbList + keywords (4 routes) |
| `routes/blog.js` | BlogPosting JSON-LD + BreadcrumbList + keywords |
| `routes/quote.js` | BreadcrumbList + keywords |
| `routes/home.js` | Keywords parameter added |
| `views/partials/head.ejs` | Meta keywords tag + JSON-LD array support |

**Total: 11 files, +802 / -244 lines**

---

## 4. Keyword Strategy

### 4.1 Primary Target Keywords

| Keyword (EN) | Keyword (FR) | Search Intent |
|-------------|-------------|---------------|
| freight forwarding Senegal | transitaire Senegal | High-intent, commercial |
| logistics company Dakar | entreprise logistique Dakar | High-intent, commercial |
| ocean freight West Africa | fret maritime Afrique de l'Ouest | Informational/commercial |
| customs clearance Senegal | dedouanement Senegal | High-intent, transactional |
| shipping company Dakar | compagnie maritime Dakar | High-intent, commercial |
| warehousing Dakar | entreposage Dakar | Commercial |
| air freight Senegal | fret aerien Senegal | Commercial |
| supply chain Africa | chaine d'approvisionnement Afrique | Informational |

### 4.2 Location Focus

All title tags and keywords emphasize:
- **City:** Dakar
- **Country:** Senegal
- **Region:** West Africa / Afrique de l'Ouest / Westafrika

This geographic targeting is critical because:
- Low competition for location-specific logistics terms
- French keywords (transitaire, dedouanement) target the dominant Francophone West African market
- "WTL" brand abbreviation saves characters for keyword inclusion

---

## 5. Recommendations for Next Steps

### 5.1 Short-term (1-2 weeks)
- [ ] Monitor Google Search Console for indexing progress after meta tag changes
- [ ] Check that all 105 sitemap URLs become indexed (currently 3/105)
- [ ] Verify structured data in Google's Rich Results Test for key pages
- [ ] Monitor Bing Webmaster Tools for IndexNow processing status

### 5.2 Medium-term (1-3 months)
- [ ] Add blog posts targeting long-tail keywords (e.g., "how to import goods into Senegal", "Dakar port shipping guide")
- [ ] Build backlinks from local directories (Senegal business directories, WAEMU trade portals)
- [ ] Add FAQ schema to more pages (services, industries) based on actual customer questions
- [ ] Consider Google Business Profile for local SEO in Dakar
- [ ] Set up Google Merchant Center if applicable for freight quote ads

### 5.3 Long-term (3-6 months)
- [ ] Target featured snippets for FAQ-style queries ("how much does shipping to Senegal cost")
- [ ] Publish case studies with location-specific content
- [ ] Build internal linking strategy between related services/industries/blog posts
- [ ] Consider adding a Portuguese language option for lusophone West Africa (Guinea-Bissau, Cape Verde)
- [ ] Implement review/testimonial schema for social proof
- [ ] Add video content with VideoObject schema

---

## 6. Deployment Details

| Item | Value |
|------|-------|
| Firebase project | wtl2026website |
| Hosting URL | https://wtl2026website.web.app |
| Custom domain | https://worldtransgroup.com |
| Deploy timestamp | February 8, 2026 |
| Cloud Function | app (us-central1, Node.js 20, 2nd Gen) |
| Function URL | https://app-q4ymsvywja-uc.a.run.app |

---

*Report generated by Claude Code on February 8, 2026*
