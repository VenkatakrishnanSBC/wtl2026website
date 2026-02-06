# CLAUDE.md

## Project Overview

WTL2026 Website — corporate website for World Trans & Logistics, a logistics/freight company based in Dakar, Senegal serving West Africa.

## Tech Stack

- **Runtime**: Node.js
- **Framework**: Express.js v5.2.1
- **Templating**: EJS v4.0.1
- **Frontend**: Vanilla JS + CSS3 (no build tools)

## Commands

- `npm start` — run production server (`node server.js`)
- `npm run dev` — run dev server with auto-reload (`node --watch server.js`)
- Server runs on port 3000 (configurable via `PORT` env var)

## Project Structure

```
server.js              # Express entry point, route registration, middleware
routes/                # Route handlers (home, services, about, contact, blog, quote, industries)
views/                 # EJS templates
  partials/            # Shared components (head, header, footer, page-hero)
  about/               # About section pages
  services/            # Service detail pages (10 services)
  contact/             # Contact/inquiry/FAQ pages
  blog/                # Blog listing and post templates
  industries/          # Industry pages
data/                  # Static data (blog posts in blog.js)
css/style.css          # Source CSS (design tokens, responsive layout)
js/main.js             # Frontend JS (menu, scroll, animations, forms)
public/                # Served static assets (css/, js/, images/)
images/                # Source image assets
```

## Key Patterns

- Routes in `routes/` export Express routers mounted in `server.js`
- Each route renders EJS views, passing a `page` variable for nav highlighting
- Partials (`head.ejs`, `header.ejs`, `footer.ejs`, `page-hero.ejs`) are included in every page
- Blog data lives in `data/blog.js` as a JS array (no database)
- Forms (quote, inquiry) handle POST and render success pages; no persistent storage
- CSS uses custom properties for theming (primary: #005be2, secondary: #026466, accent: #00ab6b)
- Frontend animations use Intersection Observer for scroll-triggered fade-ins

## Routes

| Path | Handler |
|------|---------|
| `/` | `routes/home.js` |
| `/about/*` | `routes/about.js` (overview, vision, mission, team, values, networks) |
| `/services/*` | `routes/services.js` (10 service pages) |
| `/industries/*` | `routes/industries.js` (foreign-freight, export, import) |
| `/contact/*` | `routes/contact.js` (contact, faqs, portal, inquiry, locations) |
| `/blog` | `routes/blog.js` (listing with category filter, individual posts by slug) |
| `/quote` | `routes/quote.js` (GET form, POST submission) |
