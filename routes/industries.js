const router = require('express').Router();

router.get('/', (req, res) => res.render('industries/foreign-freight', {
  title: res.locals.t('industries.mainTitle'),
  currentPage: 'industries',
  description: res.locals.t('industries.mainDescription')
}));

router.get('/foreign-freight', (req, res) => res.render('industries/foreign-freight', {
  title: res.locals.t('industries.foreignTitle'),
  currentPage: 'industries',
  description: res.locals.t('industries.foreignDescription')
}));

router.get('/export', (req, res) => res.render('industries/export', {
  title: res.locals.t('industries.exportTitle'),
  currentPage: 'industries',
  description: res.locals.t('industries.exportDescription')
}));

router.get('/import', (req, res) => res.render('industries/import', {
  title: res.locals.t('industries.importTitle'),
  currentPage: 'industries',
  description: res.locals.t('industries.importDescription')
}));

module.exports = router;
