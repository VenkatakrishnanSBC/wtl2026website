const { createT, detectLanguage, SUPPORTED_LANGS, DEFAULT_LANG } = require('../lib/i18n');

const LANG_PREFIXES = SUPPORTED_LANGS.filter(l => l !== DEFAULT_LANG); // ['fr', 'de']

/**
 * Get the URL prefix regex pattern for non-default languages.
 */
function getLangFromUrl(url) {
  for (const lang of LANG_PREFIXES) {
    if (url.startsWith('/' + lang + '/') || url === '/' + lang) return lang;
  }
  return null;
}

/**
 * Language middleware.
 * - Detects language from URL/cookie/header
 * - Auto-redirects non-English browsers to /{lang}/ on first visit (no cookie set)
 * - Injects t(), lang, langPrefix into res.locals for templates
 */
function langMiddleware(req, res, next) {
  const lang = detectLanguage(req);
  const urlLang = getLangFromUrl(req.originalUrl);

  // Auto-redirect: non-English detected via Accept-Language, no cookie set, visiting English URL
  if (lang !== DEFAULT_LANG && !urlLang && !(req.cookies && req.cookies.wtl_lang)) {
    const targetUrl = '/' + lang + (req.originalUrl === '/' ? '/' : req.originalUrl);
    return res.redirect(302, targetUrl);
  }

  const activeLang = urlLang || DEFAULT_LANG;

  res.locals.t = createT(activeLang);
  res.locals.lang = activeLang;
  res.locals.langPrefix = activeLang !== DEFAULT_LANG ? '/' + activeLang : '';
  res.locals.altLang = activeLang === 'fr' ? 'en' : 'fr'; // kept for backwards compat
  res.locals.currentPath = urlLang
    ? req.originalUrl.replace(new RegExp('^/' + urlLang), '') || '/'
    : req.originalUrl;

  next();
}

/**
 * Language toggle route handler.
 * Sets cookie and redirects to the same page in the target language.
 */
function langSwitch(req, res) {
  const targetLang = req.params.lang;
  if (!SUPPORTED_LANGS.includes(targetLang)) {
    return res.redirect('/');
  }

  const redirectPath = req.query.redirect || '/';
  res.cookie('wtl_lang', targetLang, {
    maxAge: 365 * 24 * 60 * 60 * 1000,
    httpOnly: false,
    sameSite: 'Lax',
    path: '/'
  });

  if (targetLang !== DEFAULT_LANG) {
    res.redirect('/' + targetLang + redirectPath);
  } else {
    res.redirect(redirectPath);
  }
}

module.exports = { langMiddleware, langSwitch };
