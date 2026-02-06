const router = require('express').Router();
const posts = require('../data/blog');

router.get('/', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  const recentPosts = posts.slice(0, 3).map(p => ({
    ...p,
    title: lang === 'fr' && p.fr_title ? p.fr_title : lang === 'de' && p.de_title ? p.de_title : p.title,
    excerpt: lang === 'fr' && p.fr_excerpt ? p.fr_excerpt : lang === 'de' && p.de_excerpt ? p.de_excerpt : p.excerpt,
    category: lang === 'fr' && p.fr_category ? p.fr_category : lang === 'de' && p.de_category ? p.de_category : p.category
  }));

  res.render('home', {
    title: t('home.title'),
    currentPage: 'home',
    recentPosts,
    description: t('home.description'),
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "World Trans & Logistics",
      "url": "https://worldtransgroup.com",
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://worldtransgroup.com/blog?category={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    }
  });
});

module.exports = router;
