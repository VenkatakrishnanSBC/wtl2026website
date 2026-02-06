const router = require('express').Router();

router.get('/', (req, res) => res.render('quote', {
  title: res.locals.t('quote.title'),
  currentPage: 'quote',
  description: res.locals.t('quote.description')
}));

router.post('/', (req, res) => {
  res.render('quote-success', {
    title: res.locals.t('quoteSuccess.title'),
    currentPage: 'quote',
    description: res.locals.t('quoteSuccess.description')
  });
});

module.exports = router;
