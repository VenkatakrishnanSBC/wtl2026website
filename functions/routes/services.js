const router = require('express').Router();

router.get('/', (req, res) => res.render('services/freight', {
  title: res.locals.t('services.freightTitle'),
  currentPage: 'services',
  description: res.locals.t('services.freightDescription')
}));

router.get('/freight', (req, res) => res.render('services/freight', {
  title: res.locals.t('services.airFreightTitle'),
  currentPage: 'services',
  description: res.locals.t('services.airFreightDescription')
}));

router.get('/ocean-freight', (req, res) => res.render('services/ocean-freight', {
  title: res.locals.t('services.oceanTitle'),
  currentPage: 'services',
  description: res.locals.t('services.oceanDescription')
}));

router.get('/land-freight', (req, res) => res.render('services/land-freight', {
  title: res.locals.t('services.landTitle'),
  currentPage: 'services',
  description: res.locals.t('services.landDescription')
}));

router.get('/warehousing', (req, res) => res.render('services/warehousing', {
  title: res.locals.t('services.warehousingTitle'),
  currentPage: 'services',
  description: res.locals.t('services.warehousingDescription')
}));

router.get('/nvocc', (req, res) => res.render('services/nvocc', {
  title: res.locals.t('services.nvoccTitle'),
  currentPage: 'services',
  description: res.locals.t('services.nvoccDescription')
}));

router.get('/project-cargo', (req, res) => res.render('services/project-cargo', {
  title: res.locals.t('services.projectCargoTitle'),
  currentPage: 'services',
  description: res.locals.t('services.projectCargoDescription')
}));

router.get('/door-to-door', (req, res) => res.render('services/door-to-door', {
  title: res.locals.t('services.doorToDoorTitle'),
  currentPage: 'services',
  description: res.locals.t('services.doorToDoorDescription')
}));

router.get('/inland-transportation', (req, res) => res.render('services/inland-transportation', {
  title: res.locals.t('services.inlandTitle'),
  currentPage: 'services',
  description: res.locals.t('services.inlandDescription')
}));

router.get('/forwarding', (req, res) => res.render('services/forwarding', {
  title: res.locals.t('services.forwardingTitle'),
  currentPage: 'services',
  description: res.locals.t('services.forwardingDescription')
}));

router.get('/distribution', (req, res) => res.render('services/distribution', {
  title: res.locals.t('services.distributionTitle'),
  currentPage: 'services',
  description: res.locals.t('services.distributionDescription')
}));

module.exports = router;
