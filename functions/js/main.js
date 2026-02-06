/* ==========================================================================
   WTL 2026 — Frontend Scripts
   ========================================================================== */

(function () {
  'use strict';

  /* ---------- Mobile menu ---------- */
  const menuToggle = document.getElementById('menuToggle');
  const navMenu = document.getElementById('navMenu');

  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      const icon = menuToggle.querySelector('i');
      if (icon) {
        icon.classList.toggle('fa-bars');
        icon.classList.toggle('fa-times');
      }
    });

    // Close on link click (mobile)
    navMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
          navMenu.classList.remove('active');
          const icon = menuToggle.querySelector('i');
          if (icon) {
            icon.classList.add('fa-bars');
            icon.classList.remove('fa-times');
          }
        }
      });
    });

    // Mobile dropdown toggle
    if (window.innerWidth <= 768) {
      document.querySelectorAll('.dropdown > a').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
          if (window.innerWidth <= 768) {
            e.preventDefault();
            trigger.parentElement.classList.toggle('open');
          }
        });
      });
    }
  }

  /* ---------- Sticky header ---------- */
  const header = document.querySelector('.header');
  if (header) {
    const onScroll = () => {
      header.classList.toggle('scrolled', window.scrollY > 10);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Smooth scroll ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ---------- Scroll animations ---------- */
  const animateElements = document.querySelectorAll(
    '.service-card, .why-card, .team-card, .portfolio-card, .blog-card, .stat-item, .location-card, .about-feature'
  );
  if (animateElements.length > 0) {
    animateElements.forEach(el => el.classList.add('animate-on-scroll'));

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    animateElements.forEach((el, i) => {
      el.style.transitionDelay = `${(i % 3) * 80}ms`;
      observer.observe(el);
    });
  }

  /* ---------- Counter animation ---------- */
  const counters = document.querySelectorAll('.stat-number');
  if (counters.length > 0) {
    const animateCounter = (el) => {
      const text = el.textContent.trim();
      const match = text.match(/([\d,]+)/);
      if (!match) return;
      const target = parseInt(match[1].replace(/,/g, ''), 10);
      const suffix = text.replace(match[1], '').trim();
      const duration = 1800;
      const start = performance.now();

      const step = (now) => {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(target * eased);
        el.textContent = current.toLocaleString() + suffix;
        if (progress < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };

    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    counters.forEach(c => counterObserver.observe(c));
  }

  /* ---------- Testimonial switching ---------- */
  const avatars = document.querySelectorAll('.testimonial-avatars .avatar');
  const testimonials = window.__testimonials || [
    { text: '\u201cOutstanding logistics partner that delivered our goods across three continents without a single delay. Their real-time tracking made the entire process transparent.\u201d', name: 'George D. Coffey', role: 'Architect' },
    { text: '\u201cWTL transformed our supply chain operations. Their expertise in customs clearance and warehousing solutions has been invaluable to our growing business.\u201d', name: 'Melissa J. Talley', role: 'Entrepreneur' },
    { text: '\u201cReliable, professional, and always on time. WTL has become an indispensable part of our international logistics strategy.\u201d', name: 'Wilton Groves', role: 'Operations Director' }
  ];

  if (avatars.length > 0) {
    avatars.forEach((avatar, i) => {
      avatar.addEventListener('click', () => {
        avatars.forEach(a => a.classList.remove('active'));
        avatar.classList.add('active');
        const card = document.querySelector('.testimonial-card');
        if (card && testimonials[i]) {
          card.querySelector('blockquote').textContent = testimonials[i].text;
          card.querySelector('.testimonial-author').textContent = testimonials[i].name;
          card.querySelector('.testimonial-role').textContent = testimonials[i].role;
        }
      });
    });
  }
})();
