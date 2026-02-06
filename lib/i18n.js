const fs = require('fs');
const path = require('path');

const locales = {};
const SUPPORTED_LANGS = ['en', 'fr', 'de'];
const DEFAULT_LANG = 'en';

// Load locale files
SUPPORTED_LANGS.forEach(lang => {
  const filePath = path.join(__dirname, '..', 'locales', `${lang}.json`);
  locales[lang] = JSON.parse(fs.readFileSync(filePath, 'utf8'));
});

/**
 * Create a translation function for a given language.
 * Usage: t('nav.home') => "Home" (en) or "Accueil" (fr)
 * Supports nested keys with dot notation.
 * Falls back to English, then to the key itself.
 */
function createT(lang) {
  if (!SUPPORTED_LANGS.includes(lang)) lang = DEFAULT_LANG;

  return function t(key, replacements) {
    let value = getNestedValue(locales[lang], key);
    if (value === undefined) {
      value = getNestedValue(locales[DEFAULT_LANG], key);
    }
    if (value === undefined) return key;

    if (replacements && typeof value === 'string') {
      Object.keys(replacements).forEach(k => {
        value = value.replace(new RegExp(`{{${k}}}`, 'g'), replacements[k]);
      });
    }

    return value;
  };
}

function getNestedValue(obj, key) {
  return key.split('.').reduce((o, k) => (o && o[k] !== undefined ? o[k] : undefined), obj);
}

/**
 * Detect language from request.
 * Priority: URL prefix > cookie > Accept-Language header > default
 */
function detectLanguage(req) {
  // 1. URL prefix
  if (req.originalUrl.startsWith('/fr')) return 'fr';
  if (req.originalUrl.startsWith('/de')) return 'de';

  // 2. Cookie
  if (req.cookies && req.cookies.wtl_lang) {
    const cookieLang = req.cookies.wtl_lang;
    if (SUPPORTED_LANGS.includes(cookieLang)) return cookieLang;
  }

  // 3. Accept-Language header
  const acceptLang = req.headers['accept-language'] || '';
  if (acceptLang.toLowerCase().startsWith('fr')) return 'fr';
  if (acceptLang.toLowerCase().startsWith('de')) return 'de';

  return DEFAULT_LANG;
}

module.exports = { createT, detectLanguage, SUPPORTED_LANGS, DEFAULT_LANG };
