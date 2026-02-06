# World Trans & Logistics — WordPress Site Reference

Source: `http://35.179.146.246` (WordPress 6.9, Elementor, Hello Theme)

---

## Brand

- **Site Title:** Worldtransgroup
- **Tagline:** World is our play ground
- **Copyright:** © 2024 World Trans & Logistics
- **Language:** English / Français (language switcher present)

---

## Colors

### Primary Palette (from HTML/inline styles)

| Token            | Hex       | Usage                          |
|------------------|-----------|--------------------------------|
| Dark BG          | `#0c0d0e` | Divider / dark sections        |
| Facebook         | `#3b5998` | Social icon                    |
| LinkedIn         | `#0077b5` | Social icon                    |
| Digg Blue        | `#005be2` | Social icon / accent           |
| Xing Teal        | `#026466` | Social icon                    |
| Medium Green     | `#00ab6b` | Social icon                    |
| Black            | `#000000` | WordPress preset               |
| White            | `#ffffff` | WordPress preset               |
| Cyan-Bluish Gray | `#abb8c3` | WordPress preset               |
| Vivid Cyan Blue  | `#0693e3` | WordPress preset               |
| Vivid Green Cyan | `#00d084` | WordPress preset               |

### Notes
- The WordPress CSS file could not be fully extracted (LiteSpeed cache bundle). The above colors come from inline styles, Elementor widget data, and WordPress global style presets embedded in the HTML.
- The site likely uses a primary blue in the `#0693e3` – `#005be2` range for CTAs and headings.

---

## Navigation Structure

### Top Bar
- Phone: +221 33 822 71 11
- Email: info@35.179.146.246

### Main Nav

| Menu Item         | Submenu Items                                                                                         |
|-------------------|-------------------------------------------------------------------------------------------------------|
| Home              | —                                                                                                     |
| About Us          | Overview, Our Vision, Our Mission, Our Team, Our Values, Networks                                     |
| Services          | Air Freight, Road Transport, Ocean Freight, Customs Clearance, Warehousing, Insurance, Consulting, Project Cargo, Supply Chain Management, E-commerce Logistics |
| Industries Served | Foreign to Foreign, Export, Import                                                                    |
| Customer Support  | Contact Us, FAQs, Customer Portal                                                                    |
| Contact           | Inquiry Form, Office Locations                                                                        |

### CTA Button
- **"Get a Quote"** — opens a popup/modal form

---

## Page Sections (Homepage)

### 1. Hero
- **Heading:** "Connect your business to a world of possibilities with WTL"
- **CTA Buttons:** "Get Started", "Explore"

### 2. Counter / Stats
- **25+** Years of Experience

### 3. About Company
- **Label:** About Our Company
- **Heading:** "Logistics that is Dedicated to Your Success"
- **Body:** World Trans and Logistics (WTL) is a logistics company based in Senegal, West Africa. Founded by Mr. Mamadou Sall, WTL has been a key player in the import-export and logistics industry for the past 25 years.
- **CTA:** "Read More"

### 4. What We Offer (Services)
- **Label:** What We Offer
- **Heading:** "Reliable logistics & transport solutions"
- Cards:
  1. **Air Freight** — "Efficient air freight solutions for time-sensitive shipments worldwide"
  2. **Road Transport** — "Reliable road transport services across West Africa and beyond"
  3. **Ocean Freight** — "Cost-effective ocean freight for large volume international shipments"
- Each card has a "Read More" link

### 5. Why Choose Us
- **Heading:** "Why Choose Us"
- Items:
  1. **Customer Satisfaction Tools** — "Track shipments in real-time and manage your logistics effortlessly"
  2. **Freight Payment Options** — "Flexible payment solutions for all your freight needs"
  3. **Management & Reporting** — "Comprehensive logistics management and detailed reporting"
  4. **Compliance Solutions** — "Stay compliant with international shipping regulations"

### 6. Our Team
- **Label:** Our Team
- **Heading:** "Meet Our Expert Team"
- Flip cards (front: photo + name/title, back: description):
  1. **CEO / Director General**
  2. **Finance**
  3. **Administration**
  4. **Warehouse**

### 7. CTA Banner
- **Heading:** "Logistics that is connecting you to endless possibilities"
- **Button:** "Get Started"

### 8. Our Portfolio
- **Label:** Our Portfolio
- **Heading:** "Delivering excellence in every shipment"
- Cards:
  1. **Warehousing** — "State-of-the-art warehousing facilities for secure storage"
  2. **Freight Solutions** — "Comprehensive freight solutions tailored to your needs"
  3. **Trusted Partner** — "Your trusted partner in global logistics"

### 9. Testimonials
- **Label:** Testimonials
- **Heading:** "What Our Clients Say"
- Quotes:
  1. **George D. Coffey** — Architect
  2. **Melissa J. Talley** — Entrepreneur
  3. **Wilton Groves** — Designer

### 10. Our Network (Client Logos)
- **Heading:** "Our Network"
- Carousel with 5 client logo images

---

## Footer

### Column 1 — Brand
- Logo
- "World Trans and Logistics (WTL) is your trusted partner in global logistics solutions."
- Social icons: Facebook, LinkedIn

### Column 2 — Company
- About Us
- Our Team
- Our Values
- Networks

### Column 3 — Service
- Air Freight
- Road Transport
- Ocean Freight
- Customs Clearance
- Warehousing

### Column 4 — Quick Links
- Contact Us
- FAQs
- Customer Portal
- Get a Quote

### Bottom Bar
- © 2024 World Trans & Logistics

---

## Quote Form (Popup Modal)

Fields:
- Company Name *
- Contact Person *
- Email Address *
- Phone Number
- Shipment Type * (Air Freight, Ocean Freight FCL, Ocean Freight LCL, Road Transport, Multimodal)
- Origin Country *
- Destination Country *
- Cargo Description
- Weight
- Dimensions (LxWxH)
- Preferred Shipping Date
- Incoterms (EXW, FCA, FOB, CFR, CIF, DAP, DDP)
- Additional Services: Insurance, Customs Clearance, Door-to-Door, Warehousing
- Special Handling Requirements
- Comments / Additional Info
- **Submit Button:** "Submit Quote Request"

---

## Key Differences from Current Node.js Site

| Aspect              | WordPress Site                | Current Node.js Site          |
|---------------------|-------------------------------|-------------------------------|
| Years of Experience | 25+                           | 15+ (needs update)            |
| Services count      | 10 services in nav            | 10 services in nav            |
| Team section        | Flip cards                    | Standard cards                |
| Portfolio section   | Present                       | Not present                   |
| Testimonials        | 3 testimonials                | Present                       |
| Client logos        | Carousel with 5 logos         | Present                       |
| Language switcher   | English / Français            | Not present                   |
| Quote form          | Popup modal                   | Separate /quote page          |
