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
  res.render('quote', {
    title: t('quote.title'),
    currentPage: 'quote',
    description: t('quote.description'),
    keywords: t('quote.keywords'),
    jsonLd: breadcrumb(lang, [
      { name: t('nav.home'), path: '/' },
      { name: t('nav.getQuote'), path: '/quote' }
    ])
  });
});

router.post('/', (req, res) => {
  res.render('quote-success', {
    title: res.locals.t('quoteSuccess.title'),
    currentPage: 'quote',
    description: res.locals.t('quoteSuccess.description')
  });
});

module.exports = router;
