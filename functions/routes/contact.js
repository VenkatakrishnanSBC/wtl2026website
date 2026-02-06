const router = require('express').Router();

const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How long does international shipping typically take?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Ocean Freight: 15-25 days to European ports, 30-45 days to Asian ports, 20-30 days to North American ports. Air Freight: 2-5 business days globally. Road Transport: 2-7 days for regional West African destinations."
      }
    },
    {
      "@type": "Question",
      "name": "How can I track my shipment?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "WTL provides tracking via the Customer Portal with real-time status, email notifications at key milestones, and a dedicated account manager available by phone or email."
      }
    },
    {
      "@type": "Question",
      "name": "How are customs duties and taxes calculated?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Duties are based on HS Code classification following the WAEMU Common External Tariff (0-20%), calculated on CIF value. Additional levies include 18% VAT, statistical fees, and community levies."
      }
    },
    {
      "@type": "Question",
      "name": "Do I need cargo insurance, and what does it cover?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "While not legally mandatory, WTL strongly recommends cargo insurance. Options include All-Risk Coverage, Named Perils Coverage, and War & Strikes coverage. Premiums range from 0.3% to 1.5% of cargo value."
      }
    },
    {
      "@type": "Question",
      "name": "What are the packaging requirements for international shipping?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Ocean freight requires export-grade packaging with ISPM-15 compliant wooden packaging. Air freight must meet IATA standards. Hazardous materials need UN-certified containers with proper labeling per IMDG Code or IATA DGR."
      }
    },
    {
      "@type": "Question",
      "name": "What items are prohibited or restricted for import into Senegal?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Prohibited items include narcotics, counterfeit goods, and certain weapons. Restricted items requiring special permits include pharmaceuticals, food products, chemicals, telecommunications equipment, and used vehicles over a certain age."
      }
    },
    {
      "@type": "Question",
      "name": "What are Incoterms and which one should I use?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Incoterms are standardized ICC trade rules defining buyer/seller responsibilities. Common terms include EXW, FOB, CIF (most common for Senegal imports), and DDP. WTL advises on the best Incoterm for your transaction."
      }
    },
    {
      "@type": "Question",
      "name": "What payment methods does WTL accept?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "WTL accepts bank transfers (CFA, USD, EUR), corporate credit accounts (net-15/30), letters of credit, and mobile money (Orange Money, Wave) for smaller domestic transactions."
      }
    },
    {
      "@type": "Question",
      "name": "How do I file a claim for damaged or lost cargo?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Report damage within 3 days (visible) or 15 days (concealed), file a written claim with supporting documents, WTL coordinates survey and investigation, and settlement typically occurs within 30-60 days."
      }
    },
    {
      "@type": "Question",
      "name": "What are WTL's warehousing fees and services?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "WTL offers short-term storage (per cubic meter/day), long-term warehousing (monthly rates), and specialized temperature-controlled storage. Value-added services include labeling, repackaging, kitting, and quality inspection."
      }
    }
  ]
};

router.get('/', (req, res) => res.render('contact/contact', {
  title: res.locals.t('contact.title'),
  currentPage: 'contact',
  description: res.locals.t('contact.description')
}));

router.get('/faqs', (req, res) => res.render('contact/faqs', {
  title: res.locals.t('contact.faqsTitle'),
  currentPage: 'contact',
  description: res.locals.t('contact.faqsDescription'),
  jsonLd: faqSchema
}));

router.get('/portal', (req, res) => res.render('contact/portal', {
  title: res.locals.t('contact.portalTitle'),
  currentPage: 'contact',
  description: res.locals.t('contact.portalDescription')
}));

router.get('/inquiry', (req, res) => res.render('contact/inquiry', {
  title: res.locals.t('contact.inquiryTitle'),
  currentPage: 'contact',
  description: res.locals.t('contact.inquiryDescription')
}));

router.get('/locations', (req, res) => res.render('contact/locations', {
  title: res.locals.t('contact.locationsTitle'),
  currentPage: 'contact',
  description: res.locals.t('contact.locationsDescription')
}));

router.post('/inquiry', (req, res) => {
  res.render('contact/inquiry-success', {
    title: res.locals.t('contact.inquirySuccessTitle'),
    currentPage: 'contact',
    description: res.locals.t('contact.inquirySuccessDescription')
  });
});

module.exports = router;
