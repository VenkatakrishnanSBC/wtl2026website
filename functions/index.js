const functions = require('firebase-functions');
const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const { langMiddleware, langSwitch } = require('./middleware/lang');

const app = express();
const PORT = process.env.PORT || 3000;

// View engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Static files
app.use(express.static(path.join(__dirname, 'public')));

// Body parser
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());

// SEO locals middleware
app.use((req, res, next) => {
  const urlPath = req.originalUrl.split('?')[0].replace(/\/$/, '') || '';
  res.locals.canonicalUrl = 'https://worldtransgroup.com' + urlPath;
  res.locals.ogImage = 'https://worldtransgroup.com/images/cropped-WTLS-192x192.png';
  const pathWithoutLang = urlPath.replace(/^\/(fr|de)/, '') || '/';
  res.locals.enUrl = 'https://worldtransgroup.com' + pathWithoutLang;
  res.locals.frUrl = 'https://worldtransgroup.com/fr' + (pathWithoutLang === '/' ? '/' : pathWithoutLang);
  res.locals.deUrl = 'https://worldtransgroup.com/de' + (pathWithoutLang === '/' ? '/' : pathWithoutLang);
  next();
});

// Language middleware
app.use(langMiddleware);

// Language switch route
app.get('/set-lang/:lang', langSwitch);

// Routes (English — default)
app.use('/', require('./routes/home'));
app.use('/about', require('./routes/about'));
app.use('/services', require('./routes/services'));
app.use('/industries', require('./routes/industries'));
app.use('/contact', require('./routes/contact'));
app.use('/blog', require('./routes/blog'));
app.use('/quote', require('./routes/quote'));

// Routes (French — /fr prefix, same handlers)
app.use('/fr', require('./routes/home'));
app.use('/fr/about', require('./routes/about'));
app.use('/fr/services', require('./routes/services'));
app.use('/fr/industries', require('./routes/industries'));
app.use('/fr/contact', require('./routes/contact'));
app.use('/fr/blog', require('./routes/blog'));
app.use('/fr/quote', require('./routes/quote'));

// Routes (German — /de prefix, same handlers)
app.use('/de', require('./routes/home'));
app.use('/de/about', require('./routes/about'));
app.use('/de/services', require('./routes/services'));
app.use('/de/industries', require('./routes/industries'));
app.use('/de/contact', require('./routes/contact'));
app.use('/de/blog', require('./routes/blog'));
app.use('/de/quote', require('./routes/quote'));

// 404 handler
app.use((req, res) => {
  res.status(404).render('404', {
    title: res.locals.t('404.title'),
    currentPage: '',
    description: res.locals.t('404.description')
  });
});

// Export for Firebase Functions
exports.app = functions.https.onRequest(app);

// For local testing
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`WTL website running at http://localhost:${PORT}`);
  });
}
