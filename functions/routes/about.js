const router = require('express').Router();

const DOMAIN = 'https://worldtransgroup.com';

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
  res.render('about/overview', {
    title: t('about.overviewTitle'),
    currentPage: 'about',
    description: t('about.overviewDescription'),
    keywords: t('about.overviewKeywords'),
    jsonLd: breadcrumb(lang, [
      { name: t('nav.home'), path: '/' },
      { name: t('nav.about'), path: '/about' }
    ])
  });
});

router.get('/overview', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('about/overview', {
    title: t('about.overviewTitle2'),
    currentPage: 'about',
    description: t('about.overviewDescription2'),
    keywords: t('about.overviewKeywords'),
    jsonLd: breadcrumb(lang, [
      { name: t('nav.home'), path: '/' },
      { name: t('nav.about'), path: '/about' },
      { name: t('nav.overview'), path: '/about/overview' }
    ])
  });
});

router.get('/vision', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('about/vision', {
    title: t('about.visionTitle'),
    currentPage: 'about',
    description: t('about.visionDescription'),
    keywords: t('about.visionKeywords'),
    jsonLd: breadcrumb(lang, [
      { name: t('nav.home'), path: '/' },
      { name: t('nav.about'), path: '/about' },
      { name: t('nav.vision'), path: '/about/vision' }
    ])
  });
});

router.get('/mission', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('about/mission', {
    title: t('about.missionTitle'),
    currentPage: 'about',
    description: t('about.missionDescription'),
    keywords: t('about.missionKeywords'),
    jsonLd: breadcrumb(lang, [
      { name: t('nav.home'), path: '/' },
      { name: t('nav.about'), path: '/about' },
      { name: t('nav.mission'), path: '/about/mission' }
    ])
  });
});

router.get('/team', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('about/team', {
    title: t('about.teamTitle'),
    currentPage: 'about',
    description: t('about.teamDescription'),
    keywords: t('about.teamKeywords'),
    jsonLd: breadcrumb(lang, [
      { name: t('nav.home'), path: '/' },
      { name: t('nav.about'), path: '/about' },
      { name: t('nav.team'), path: '/about/team' }
    ])
  });
});

router.get('/values', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('about/values', {
    title: t('about.valuesTitle'),
    currentPage: 'about',
    description: t('about.valuesDescription'),
    keywords: t('about.valuesKeywords'),
    jsonLd: breadcrumb(lang, [
      { name: t('nav.home'), path: '/' },
      { name: t('nav.about'), path: '/about' },
      { name: t('nav.values'), path: '/about/values' }
    ])
  });
});

router.get('/networks', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('about/networks', {
    title: t('about.networksTitle'),
    currentPage: 'about',
    description: t('about.networksDescription'),
    keywords: t('about.networksKeywords'),
    jsonLd: breadcrumb(lang, [
      { name: t('nav.home'), path: '/' },
      { name: t('nav.about'), path: '/about' },
      { name: t('nav.networks'), path: '/about/networks' }
    ])
  });
});

module.exports = router;
