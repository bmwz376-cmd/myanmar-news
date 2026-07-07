/* ============================================
   NL-DG Corporate Website - app.js
   Features: smooth scroll, sticky header,
   hamburger menu, news filter, form validation
   ============================================ */

(function () {
  'use strict';

  // ============ Sticky Header ============
  const header = document.getElementById('site-header');

  function handleScroll() {
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }

    // Back to top button
    const backToTop = document.getElementById('back-to-top');
    if (backToTop) {
      if (window.scrollY > 400) {
        backToTop.classList.add('visible');
      } else {
        backToTop.classList.remove('visible');
      }
    }
  }

  window.addEventListener('scroll', handleScroll, { passive: true });

  // ============ Smooth Scroll ============
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;

      const target = document.querySelector(targetId);
      if (!target) return;

      e.preventDefault();

      const headerHeight = header ? header.offsetHeight : 0;
      const targetTop = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;

      window.scrollTo({
        top: targetTop,
        behavior: 'smooth'
      });

      // Close mobile nav if open
      closeMobileNav();
    });
  });

  // ============ Hamburger Menu ============
  const hamburger = document.getElementById('hamburger');
  const mainNav = document.getElementById('main-nav');

  function closeMobileNav() {
    if (hamburger && mainNav) {
      hamburger.classList.remove('active');
      mainNav.classList.remove('open');
      document.body.style.overflow = '';
    }
  }

  if (hamburger && mainNav) {
    hamburger.addEventListener('click', function () {
      const isOpen = mainNav.classList.contains('open');
      if (isOpen) {
        closeMobileNav();
      } else {
        hamburger.classList.add('active');
        mainNav.classList.add('open');
        document.body.style.overflow = 'hidden';
      }
    });

    // Close nav when clicking outside
    document.addEventListener('click', function (e) {
      if (
        mainNav.classList.contains('open') &&
        !mainNav.contains(e.target) &&
        !hamburger.contains(e.target)
      ) {
        closeMobileNav();
      }
    });
  }

  // ============ News Category Filter ============
  const filterButtons = document.querySelectorAll('.filter-btn');
  const newsCards = document.querySelectorAll('.news-card');

  filterButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      // Update active button
      filterButtons.forEach(function (b) { b.classList.remove('active'); });
      this.classList.add('active');

      const filter = this.getAttribute('data-filter');

      newsCards.forEach(function (card) {
        const category = card.getAttribute('data-category');

        if (filter === 'all' || category === filter) {
          card.classList.remove('hidden');
          // Re-animate
          card.style.animation = 'none';
          card.offsetHeight; // reflow
          card.style.animation = '';
        } else {
          card.classList.add('hidden');
        }
      });
    });
  });

  // ============ Form Validation ============
  const form = document.getElementById('contact-form');

  if (form) {
    const fields = {
      name: {
        el: document.getElementById('name'),
        error: document.getElementById('name-error'),
        validate: function (val) {
          if (!val.trim()) return 'お名前を入力してください。';
          if (val.trim().length < 2) return 'お名前は2文字以上で入力してください。';
          return '';
        }
      },
      email: {
        el: document.getElementById('email'),
        error: document.getElementById('email-error'),
        validate: function (val) {
          if (!val.trim()) return 'メールアドレスを入力してください。';
          const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRe.test(val.trim())) return '正しいメールアドレスを入力してください。';
          return '';
        }
      },
      service: {
        el: document.getElementById('service'),
        error: document.getElementById('service-error'),
        validate: function (val) {
          if (!val) return 'お問い合わせ内容を選択してください。';
          return '';
        }
      },
      message: {
        el: document.getElementById('message'),
        error: document.getElementById('message-error'),
        validate: function (val) {
          if (!val.trim()) return 'メッセージを入力してください。';
          if (val.trim().length < 10) return 'メッセージは10文字以上で入力してください。';
          return '';
        }
      }
    };

    // Real-time validation on blur
    Object.keys(fields).forEach(function (key) {
      const field = fields[key];
      if (field.el) {
        field.el.addEventListener('blur', function () {
          const errorMsg = field.validate(this.value);
          if (errorMsg) {
            field.error.textContent = errorMsg;
            field.el.classList.add('error');
          } else {
            field.error.textContent = '';
            field.el.classList.remove('error');
          }
        });

        field.el.addEventListener('input', function () {
          if (field.el.classList.contains('error')) {
            const errorMsg = field.validate(this.value);
            if (!errorMsg) {
              field.error.textContent = '';
              field.el.classList.remove('error');
            }
          }
        });
      }
    });

    // Privacy checkbox
    const privacyCheck = document.getElementById('privacy');
    const privacyError = document.getElementById('privacy-error');

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      let isValid = true;

      // Validate all fields
      Object.keys(fields).forEach(function (key) {
        const field = fields[key];
        if (field.el) {
          const errorMsg = field.validate(field.el.value);
          if (errorMsg) {
            field.error.textContent = errorMsg;
            field.el.classList.add('error');
            isValid = false;
          } else {
            field.error.textContent = '';
            field.el.classList.remove('error');
          }
        }
      });

      // Privacy checkbox
      if (privacyCheck && !privacyCheck.checked) {
        if (privacyError) {
          privacyError.textContent = 'プライバシーポリシーへの同意が必要です。';
        }
        isValid = false;
      } else if (privacyError) {
        privacyError.textContent = '';
      }

      if (!isValid) {
        // Scroll to first error
        const firstError = form.querySelector('.error');
        if (firstError) {
          const headerHeight = header ? header.offsetHeight : 0;
          const top = firstError.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;
          window.scrollTo({ top: top, behavior: 'smooth' });
        }
        return;
      }

      // Simulate submission
      const btnText = form.querySelector('.btn-text');
      const btnLoading = form.querySelector('.btn-loading');
      const submitBtn = form.querySelector('button[type="submit"]');
      const successMsg = document.getElementById('form-success');

      submitBtn.disabled = true;
      if (btnText) btnText.style.display = 'none';
      if (btnLoading) btnLoading.style.display = 'inline';

      setTimeout(function () {
        submitBtn.disabled = false;
        if (btnText) btnText.style.display = 'inline';
        if (btnLoading) btnLoading.style.display = 'none';

        if (successMsg) {
          successMsg.style.display = 'block';
          successMsg.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        form.reset();
        Object.keys(fields).forEach(function (key) {
          const field = fields[key];
          if (field.el) field.el.classList.remove('error');
          if (field.error) field.error.textContent = '';
        });
      }, 1400);
    });
  }

  // ============ Scroll Animations ============
  function initScrollAnimations() {
    const animatedElements = document.querySelectorAll(
      '.service-card, .news-card, .stat-card, .about-text, .about-stats, .info-item'
    );

    animatedElements.forEach(function (el) {
      el.classList.add('fade-in');
    });

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px'
      }
    );

    animatedElements.forEach(function (el) {
      observer.observe(el);
    });
  }

  // Run after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initScrollAnimations);
  } else {
    initScrollAnimations();
  }

  // ============ Active Nav Highlight ============
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.main-nav a[href^="#"]');

  function updateActiveNav() {
    const scrollY = window.pageYOffset;
    const headerH = header ? header.offsetHeight : 0;

    sections.forEach(function (section) {
      const sectionTop = section.offsetTop - headerH - 80;
      const sectionBottom = sectionTop + section.offsetHeight;

      if (scrollY >= sectionTop && scrollY < sectionBottom) {
        navLinks.forEach(function (link) {
          link.classList.remove('active-nav');
          if (link.getAttribute('href') === '#' + section.id) {
            link.classList.add('active-nav');
          }
        });
      }
    });
  }

  window.addEventListener('scroll', updateActiveNav, { passive: true });

  console.log('NL-DG Website initialized');
})();
