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
  res.render('industries/foreign-freight', {
    title: t('industries.mainTitle'),
    currentPage: 'industries',
    description: t('industries.mainDescription'),
    keywords: t('industries.mainKeywords'),
    jsonLd: breadcrumb(lang, [
      { name: t('nav.home'), path: '/' },
      { name: t('nav.industries'), path: '/industries' }
    ])
  });
});

router.get('/foreign-freight', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('industries/foreign-freight', {
    title: t('industries.foreignTitle'),
    currentPage: 'industries',
    description: t('industries.foreignDescription'),
    keywords: t('industries.foreignKeywords'),
    jsonLd: breadcrumb(lang, [
      { name: t('nav.home'), path: '/' },
      { name: t('nav.industries'), path: '/industries' },
      { name: t('nav.foreignFreight'), path: '/industries/foreign-freight' }
    ])
  });
});

router.get('/export', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('industries/export', {
    title: t('industries.exportTitle'),
    currentPage: 'industries',
    description: t('industries.exportDescription'),
    keywords: t('industries.exportKeywords'),
    jsonLd: breadcrumb(lang, [
      { name: t('nav.home'), path: '/' },
      { name: t('nav.industries'), path: '/industries' },
      { name: t('nav.export'), path: '/industries/export' }
    ])
  });
});

router.get('/import', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  res.render('industries/import', {
    title: t('industries.importTitle'),
    currentPage: 'industries',
    description: t('industries.importDescription'),
    keywords: t('industries.importKeywords'),
    jsonLd: breadcrumb(lang, [
      { name: t('nav.home'), path: '/' },
      { name: t('nav.industries'), path: '/industries' },
      { name: t('nav.import'), path: '/industries/import' }
    ])
  });
});

module.exports = router;
