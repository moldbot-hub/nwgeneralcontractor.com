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

  // Footer accordion on mobile
  if (window.innerWidth <= 768) {
    document.querySelectorAll('.footer-col h4').forEach(function(heading) {
      // Skip the first footer col (company info — always open)
      if (heading.closest('.footer-col') === document.querySelector('.footer-col')) return;

      heading.addEventListener('click', function() {
        this.closest('.footer-col').classList.toggle('active');
      });
    });
  }

  // Close mobile menu when clicking outside
  document.addEventListener('click', function(e) {
    if (nav && nav.classList.contains('active')) {
      if (!nav.contains(e.target) && !toggle.contains(e.target)) {
        nav.classList.remove('active');
        toggle.classList.remove('active');
      }
    }
  });

  // CRM lead capture — send form data directly to SetMate.ai
  var SETMATE_WEBHOOK = 'https://contractormate.ai/api/public/contractor-lead';
  var SETMATE_API_KEY = 'cm_lead_8b0148dfb9275ea8d8';

  document.querySelectorAll('form[action*="formspree.io"], form.contact-form').forEach(function(form) {
    // Honeypot. Off-screen rather than display:none, which some bots skip.
    if (!form.querySelector('[name="company_website"]')) {
      var hp = document.createElement('input');
      hp.type = 'text'; hp.name = 'company_website'; hp.tabIndex = -1;
      hp.setAttribute('autocomplete', 'off'); hp.setAttribute('aria-hidden', 'true');
      hp.style.cssText = 'position:absolute;left:-9999px;width:1px;height:1px;opacity:0;';
      form.appendChild(hp);
    }

    // A2P 10DLC SMS consent — inject an optional opt-in if the form lacks one.
    // (contact.html ships a static sms_optin block, so it is skipped here.)
    if (!form.querySelector('[name="sms_optin"], [name="sms_consent"]')) {
      var smsLabel = document.createElement('label');
      smsLabel.style.cssText = 'display:flex;gap:8px;align-items:flex-start;font-size:0.8rem;color:#555;line-height:1.45;margin:0 0 14px;font-weight:400;cursor:pointer;';
      var smsCb = document.createElement('input');
      smsCb.type = 'checkbox'; smsCb.name = 'sms_consent'; smsCb.value = 'yes';
      smsCb.style.cssText = 'width:auto;margin-top:3px;flex:0 0 auto;';
      var smsSpan = document.createElement('span');
      smsSpan.innerHTML = 'I agree to receive SMS text messages from NW Style Homes 1 LLC (dba NW General Contractor) at the phone number provided regarding my project inquiry, appointment confirmations, estimates, and follow-up communications. Message frequency varies. Message &amp; data rates may apply. Reply <strong>STOP</strong> to unsubscribe or <strong>HELP</strong> for help. Consent is not a condition of purchase. We will not share your mobile information with third parties for promotional or marketing purposes.';
      smsLabel.appendChild(smsCb); smsLabel.appendChild(smsSpan);
      var smsBtn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (smsBtn && smsBtn.parentNode) { smsBtn.parentNode.insertBefore(smsLabel, smsBtn); }
      else { form.appendChild(smsLabel); }
    }
    form.addEventListener('submit', function(e) {
      e.preventDefault();

      var btn = form.querySelector('button[type="submit"]');
      var originalText = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Submitting...'; }

      var data = {};
      var formData = new FormData(form);
      formData.forEach(function(value, key) { data[key] = value; });

      // Auto-detect service from page URL if the form doesn't have a service field
      var detectedService = data.service || '';
      if (!detectedService) {
        var path = window.location.pathname.toLowerCase();
        if (path.indexOf('kitchen') !== -1) detectedService = 'kitchen';
        else if (path.indexOf('bathroom') !== -1) detectedService = 'bathroom';
        else if (path.indexOf('adu') !== -1) detectedService = 'adu';
        else if (path.indexOf('addition') !== -1) detectedService = 'addition';
        else if (path.indexOf('deck') !== -1) detectedService = 'deck';
        else if (path.indexOf('whole-home') !== -1 || path.indexOf('renovation') !== -1) detectedService = 'whole-home';
        else if (path.indexOf('carpentry') !== -1) detectedService = 'carpentry';
        else if (path.indexOf('siding') !== -1) detectedService = 'siding';
        else if (path.indexOf('window') !== -1) detectedService = 'windows';
        else if (path.indexOf('roofing') !== -1 || path.indexOf('roof') !== -1) detectedService = 'roofing';
      }

      // One id per form element, minted on first submit and REUSED on every retry.
      // Without it the server mints a fresh uuid per request, so its dedup never engages
      // for real traffic: a visitor who clicks Submit twice (which both error paths below
      // invite, by re-enabling the button) gets one contact but two opportunities and two
      // owner alerts.
      if (!form._cmRequestId) {
        form._cmRequestId = (window.crypto && window.crypto.randomUUID)
          ? window.crypto.randomUUID()
          : 'r-' + Date.now() + '-' + Math.random().toString(16).slice(2);
      }

      var payload = {
        requestId: form._cmRequestId,
        sms_consent: (data.sms_optin || data.sms_consent) ? 'yes' : 'no',
        name: data.name || '',
        email: data.email || '',
        phone: data.phone || '',
        message: data.message || '',
        service: detectedService,
        city: data.city || '',
        source: window.location.pathname,
        tracking: window._smTracking ? window._smTracking.getData() : null
      };

      fetch(SETMATE_WEBHOOK, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': SETMATE_API_KEY,
          'idempotency-key': form._cmRequestId
        },
        body: JSON.stringify(payload)
      }).then(function(res) {
        if (res.ok) {
          if (window._smTracking) window._smTracking.clear();
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
