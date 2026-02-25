/* ==========================================================================
   NW General Contractor - Main JavaScript
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {

  // Mobile menu toggle
  const toggle = document.querySelector('.mobile-toggle');
  const nav = document.querySelector('nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function() {
      toggle.classList.toggle('active');
      nav.classList.toggle('active');
    });
  }

  // Mobile dropdown toggles
  document.querySelectorAll('.dropdown > a').forEach(function(link) {
    link.addEventListener('click', function(e) {
      if (window.innerWidth <= 768) {
        e.preventDefault();
        this.parentElement.classList.toggle('active');
      }
    });
  });

  // Close mobile menu when clicking a link
  document.querySelectorAll('nav a').forEach(function(link) {
    link.addEventListener('click', function() {
      if (!this.parentElement.classList.contains('dropdown')) {
        if (toggle) toggle.classList.remove('active');
        if (nav) nav.classList.remove('active');
      }
    });
  });

  // FAQ accordion
  document.querySelectorAll('.faq-question').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var item = this.parentElement;
      var answer = item.querySelector('.faq-answer');
      var inner = answer.querySelector('.faq-answer-inner');

      // Close other items
      document.querySelectorAll('.faq-item.active').forEach(function(other) {
        if (other !== item) {
          other.classList.remove('active');
          other.querySelector('.faq-answer').style.maxHeight = '0';
        }
      });

      item.classList.toggle('active');
      if (item.classList.contains('active')) {
        answer.style.maxHeight = inner.scrollHeight + 'px';
      } else {
        answer.style.maxHeight = '0';
      }
    });
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(function(link) {
    link.addEventListener('click', function(e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        var offset = 80;
        var top = target.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top: top, behavior: 'smooth' });
      }
    });
  });

  // Scroll-triggered animations
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.service-card, .feature-item, .testimonial-card, .blog-card').forEach(function(el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

  // Add visible class styles
  var style = document.createElement('style');
  style.textContent = '.visible { opacity: 1 !important; transform: translateY(0) !important; }';
  document.head.appendChild(style);

  // Header background on scroll
  var header = document.querySelector('header');
  if (header) {
    window.addEventListener('scroll', function() {
      if (window.scrollY > 50) {
        header.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
      } else {
        header.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
      }
    });
  }

  // CRM lead capture — send form data directly to SetMate.ai
  var SETMATE_WEBHOOK = 'https://www.setmate.ai/api/webhooks/website-lead';
  var SETMATE_API_KEY = 'nwgc_lead_2026_sk';

  document.querySelectorAll('form[action*="formspree.io"], form.contact-form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();

      var btn = form.querySelector('button[type="submit"]');
      var originalText = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Submitting...'; }

      var data = {};
      var formData = new FormData(form);
      formData.forEach(function(value, key) { data[key] = value; });

      var payload = {
        name: data.name || '',
        email: data.email || '',
        phone: data.phone || '',
        message: data.message || '',
        service: data.service || '',
        city: data.city || '',
        source: window.location.pathname
      };

      fetch(SETMATE_WEBHOOK, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': SETMATE_API_KEY
        },
        body: JSON.stringify(payload)
      }).then(function(res) {
        if (res.ok) {
          form.innerHTML = '<div style="text-align:center;padding:2rem 1rem;">'
            + '<h3 style="color:#1a5632;margin-bottom:0.5rem;">Thank You!</h3>'
            + '<p style="color:#555;">We received your request and will get back to you within 24 hours.</p>'
            + '<p style="color:#555;">Need immediate help? Call <a href="tel:+14252865639" style="color:#d35400;font-weight:700;">(425) 286-5639</a></p>'
            + '</div>';
        } else {
          res.json().then(function(d) {
            alert('Something went wrong: ' + (d.error || 'Please try again.'));
          }).catch(function() { alert('Something went wrong. Please call us at (425) 286-5639.'); });
          if (btn) { btn.disabled = false; btn.textContent = originalText; }
        }
      }).catch(function() {
        alert('Network error. Please call us at (425) 286-5639.');
        if (btn) { btn.disabled = false; btn.textContent = originalText; }
      });
    });
  });

});
