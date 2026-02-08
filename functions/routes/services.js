const router = require('express').Router();

const DOMAIN = 'https://worldtransgroup.com';

function serviceJsonLd(name, description, url) {
  return {
    "@context": "https://schema.org",
    "@type": "Service",
    "serviceType": name,
    "provider": {
      "@type": "Organization",
      "name": "World Trans & Logistics",
      "url": DOMAIN
    },
    "areaServed": [
      { "@type": "Place", "name": "Senegal" },
      { "@type": "Place", "name": "West Africa" }
    ],
    "description": description,
    "url": url
  };
}

function breadcrumb(lang, items) {
  const prefix = lang === 'fr' ? '/fr' : lang === 'de' ? '/de' : '';
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": items.map((item, i) => ({
      "@type": "ListItem",
      "position": i + 1,
      "name": item.name,
      "item": DOMAIN + prefix + item.path
    }))
  };
}

router.get('/', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('services/freight', {
    title: t('services.freightTitle'),
    currentPage: 'services',
    description: t('services.freightDescription'),
    keywords: t('services.freightKeywords'),
    jsonLd: [
      serviceJsonLd('Air Freight', t('services.freightDescription'), DOMAIN + '/services'),
      breadcrumb(lang, [
        { name: t('nav.home'), path: '/' },
        { name: t('nav.services'), path: '/services' }
      ])
    ]
  });
});

router.get('/freight', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('services/freight', {
    title: t('services.airFreightTitle'),
    currentPage: 'services',
    description: t('services.airFreightDescription'),
    keywords: t('services.airFreightKeywords'),
    jsonLd: [
      serviceJsonLd('Air Freight', t('services.airFreightDescription'), DOMAIN + '/services/freight'),
      breadcrumb(lang, [
        { name: t('nav.home'), path: '/' },
        { name: t('nav.services'), path: '/services' },
        { name: t('nav.freight'), path: '/services/freight' }
      ])
    ]
  });
});

router.get('/ocean-freight', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('services/ocean-freight', {
    title: t('services.oceanTitle'),
    currentPage: 'services',
    description: t('services.oceanDescription'),
    keywords: t('services.oceanKeywords'),
    jsonLd: [
      serviceJsonLd('Ocean Freight', t('services.oceanDescription'), DOMAIN + '/services/ocean-freight'),
      breadcrumb(lang, [
        { name: t('nav.home'), path: '/' },
        { name: t('nav.services'), path: '/services' },
        { name: t('nav.oceanFreight'), path: '/services/ocean-freight' }
      ])
    ]
  });
});

router.get('/land-freight', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('services/land-freight', {
    title: t('services.landTitle'),
    currentPage: 'services',
    description: t('services.landDescription'),
    keywords: t('services.landKeywords'),
    jsonLd: [
      serviceJsonLd('Land & Rail Freight', t('services.landDescription'), DOMAIN + '/services/land-freight'),
      breadcrumb(lang, [
        { name: t('nav.home'), path: '/' },
        { name: t('nav.services'), path: '/services' },
        { name: t('nav.landFreight'), path: '/services/land-freight' }
      ])
    ]
  });
});

router.get('/warehousing', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('services/warehousing', {
    title: t('services.warehousingTitle'),
    currentPage: 'services',
    description: t('services.warehousingDescription'),
    keywords: t('services.warehousingKeywords'),
    jsonLd: [
      serviceJsonLd('Warehousing & Storage', t('services.warehousingDescription'), DOMAIN + '/services/warehousing'),
      breadcrumb(lang, [
        { name: t('nav.home'), path: '/' },
        { name: t('nav.services'), path: '/services' },
        { name: t('nav.warehousing'), path: '/services/warehousing' }
      ])
    ]
  });
});

router.get('/nvocc', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('services/nvocc', {
    title: t('services.nvoccTitle'),
    currentPage: 'services',
    description: t('services.nvoccDescription'),
    keywords: t('services.nvoccKeywords'),
    jsonLd: [
      serviceJsonLd('NVOCC', t('services.nvoccDescription'), DOMAIN + '/services/nvocc'),
      breadcrumb(lang, [
        { name: t('nav.home'), path: '/' },
        { name: t('nav.services'), path: '/services' },
        { name: t('nav.nvocc'), path: '/services/nvocc' }
      ])
    ]
  });
});

router.get('/project-cargo', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('services/project-cargo', {
    title: t('services.projectCargoTitle'),
    currentPage: 'services',
    description: t('services.projectCargoDescription'),
    keywords: t('services.projectCargoKeywords'),
    jsonLd: [
      serviceJsonLd('Project Cargo', t('services.projectCargoDescription'), DOMAIN + '/services/project-cargo'),
      breadcrumb(lang, [
        { name: t('nav.home'), path: '/' },
        { name: t('nav.services'), path: '/services' },
        { name: t('nav.projectCargo'), path: '/services/project-cargo' }
      ])
    ]
  });
});

router.get('/door-to-door', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('services/door-to-door', {
    title: t('services.doorToDoorTitle'),
    currentPage: 'services',
    description: t('services.doorToDoorDescription'),
    keywords: t('services.doorToDoorKeywords'),
    jsonLd: [
      serviceJsonLd('Door-to-Door Delivery', t('services.doorToDoorDescription'), DOMAIN + '/services/door-to-door'),
      breadcrumb(lang, [
        { name: t('nav.home'), path: '/' },
        { name: t('nav.services'), path: '/services' },
        { name: t('nav.doorToDoor'), path: '/services/door-to-door' }
      ])
    ]
  });
});

router.get('/inland-transportation', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('services/inland-transportation', {
    title: t('services.inlandTitle'),
    currentPage: 'services',
    description: t('services.inlandDescription'),
    keywords: t('services.inlandKeywords'),
    jsonLd: [
      serviceJsonLd('Inland Transportation', t('services.inlandDescription'), DOMAIN + '/services/inland-transportation'),
      breadcrumb(lang, [
        { name: t('nav.home'), path: '/' },
        { name: t('nav.services'), path: '/services' },
        { name: t('nav.inlandTransportation'), path: '/services/inland-transportation' }
      ])
    ]
  });
});

router.get('/forwarding', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('services/forwarding', {
    title: t('services.forwardingTitle'),
    currentPage: 'services',
    description: t('services.forwardingDescription'),
    keywords: t('services.forwardingKeywords'),
    jsonLd: [
      serviceJsonLd('Freight Forwarding', t('services.forwardingDescription'), DOMAIN + '/services/forwarding'),
      breadcrumb(lang, [
        { name: t('nav.home'), path: '/' },
        { name: t('nav.services'), path: '/services' },
        { name: t('nav.forwarding'), path: '/services/forwarding' }
      ])
    ]
  });
});

router.get('/distribution', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('services/distribution', {
    title: t('services.distributionTitle'),
    currentPage: 'services',
    description: t('services.distributionDescription'),
    keywords: t('services.distributionKeywords'),
    jsonLd: [
      serviceJsonLd('Distribution', t('services.distributionDescription'), DOMAIN + '/services/distribution'),
      breadcrumb(lang, [
        { name: t('nav.home'), path: '/' },
        { name: t('nav.services'), path: '/services' },
        { name: t('nav.distribution'), path: '/services/distribution' }
      ])
    ]
  });
});

module.exports = router;
