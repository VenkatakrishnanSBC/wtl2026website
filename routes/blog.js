const router = require('express').Router();
const posts = require('../data/blog');

router.get('/', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  const category = req.query.category;

  const localizedPosts = posts.map(p => ({
    ...p,
    title: lang === 'fr' && p.fr_title ? p.fr_title : lang === 'de' && p.de_title ? p.de_title : p.title,
    excerpt: lang === 'fr' && p.fr_excerpt ? p.fr_excerpt : lang === 'de' && p.de_excerpt ? p.de_excerpt : p.excerpt,
    category: lang === 'fr' && p.fr_category ? p.fr_category : lang === 'de' && p.de_category ? p.de_category : p.category
  }));

  let filtered = localizedPosts;
  if (category) {
    filtered = localizedPosts.filter(p => p.category === category);
  }
  const categories = [...new Set(localizedPosts.map(p => p.category))];

  res.render('blog/index', {
    title: t('blog.title'),
    currentPage: 'blog',
    posts: filtered,
    categories,
    activeCategory: category || '',
    description: t('blog.description')
  });
});

router.get('/:slug', (req, res) => {
  const t = res.locals.t;
  const lang = res.locals.lang;
  const post = posts.find(p => p.slug === req.params.slug);
  if (!post) return res.status(404).render('404', {
    title: t('404.title'),
    currentPage: '',
    description: t('404.description')
  });

  const localizedPost = {
    ...post,
    title: lang === 'fr' && post.fr_title ? post.fr_title : lang === 'de' && post.de_title ? post.de_title : post.title,
    excerpt: lang === 'fr' && post.fr_excerpt ? post.fr_excerpt : lang === 'de' && post.de_excerpt ? post.de_excerpt : post.excerpt,
    content: lang === 'fr' && post.fr_content ? post.fr_content : lang === 'de' && post.de_content ? post.de_content : post.content,
    category: lang === 'fr' && post.fr_category ? post.fr_category : lang === 'de' && post.de_category ? post.de_category : post.category
  };

  const related = posts
    .filter(p => p.id !== post.id && p.category === post.category)
    .slice(0, 2)
    .map(p => ({
      ...p,
      title: lang === 'fr' && p.fr_title ? p.fr_title : lang === 'de' && p.de_title ? p.de_title : p.title
    }));

  res.render('blog/post', {
    title: localizedPost.title + ' — WTL Blog',
    currentPage: 'blog',
    post: localizedPost,
    related,
    description: localizedPost.excerpt,
    ogImage: 'https://worldtransgroup.com/images/' + post.image
  });
});

module.exports = router;
