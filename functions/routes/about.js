const router = require('express').Router();

router.get('/', (req, res) => res.render('about/overview', {
  title: res.locals.t('about.overviewTitle'),
  currentPage: 'about',
  description: res.locals.t('about.overviewDescription')
}));

router.get('/overview', (req, res) => res.render('about/overview', {
  title: res.locals.t('about.overviewTitle2'),
  currentPage: 'about',
  description: res.locals.t('about.overviewDescription2')
}));

router.get('/vision', (req, res) => res.render('about/vision', {
  title: res.locals.t('about.visionTitle'),
  currentPage: 'about',
  description: res.locals.t('about.visionDescription')
}));

router.get('/mission', (req, res) => res.render('about/mission', {
  title: res.locals.t('about.missionTitle'),
  currentPage: 'about',
  description: res.locals.t('about.missionDescription')
}));

router.get('/team', (req, res) => res.render('about/team', {
  title: res.locals.t('about.teamTitle'),
  currentPage: 'about',
  description: res.locals.t('about.teamDescription')
}));

router.get('/values', (req, res) => res.render('about/values', {
  title: res.locals.t('about.valuesTitle'),
  currentPage: 'about',
  description: res.locals.t('about.valuesDescription')
}));

router.get('/networks', (req, res) => res.render('about/networks', {
  title: res.locals.t('about.networksTitle'),
  currentPage: 'about',
  description: res.locals.t('about.networksDescription')
}));

module.exports = router;
