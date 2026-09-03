/* Workshop UI: progressive reveal, blueprint drawing, parallax, counters. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var mobileLayout = window.matchMedia('(max-width: 899px)');
  var revealItems = document.querySelectorAll('.reveal');
  var blueprintStages = document.querySelectorAll('.blueprint-stage');

  function show(el) {
    el.classList.add('is-visible');
    if (el.classList.contains('blueprint-stage')) el.classList.add('is-drawn');
  }

  if (reduced.matches || !('IntersectionObserver' in window)) {
    revealItems.forEach(show);
    blueprintStages.forEach(show);
  } else {
    var observer = new IntersectionObserver(function (entries, activeObserver) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        show(entry.target);
        activeObserver.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    revealItems.forEach(function (el) { observer.observe(el); });
    blueprintStages.forEach(function (el) { observer.observe(el); });
  }

  document.querySelectorAll('details.faq-item').forEach(function (item) {
    item.addEventListener('toggle', function () {
      if (!item.open) return;
      document.querySelectorAll('details.faq-item[open]').forEach(function (other) {
        if (other !== item) {
          other.open = false;
          other.classList.remove('active');
        }
      });
    });
  });

  function setCounter(el, value) {
    var prefix = el.getAttribute('data-prefix') || '';
    var suffix = el.getAttribute('data-suffix') || '';
    el.textContent = prefix + Math.round(value).toLocaleString('en-US') + suffix;
  }

  document.querySelectorAll('[data-count]').forEach(function (counter) {
    var target = Number(counter.getAttribute('data-count'));
    if (!isFinite(target)) return;
    if (reduced.matches || !('IntersectionObserver' in window)) {
      setCounter(counter, target);
      return;
    }
    var counterObserver = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting) return;
      counterObserver.disconnect();
      var start;
      function tick(time) {
        if (!start) start = time;
        var progress = Math.min((time - start) / 700, 1);
        setCounter(counter, target * (1 - Math.pow(1 - progress, 3)));
        if (progress < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }, { threshold: 0.5 });
    counterObserver.observe(counter);
  });

  var hero = document.querySelector('.blueprint-hero');
  var processRail = document.querySelector('.process-rail');
  var ticking = false;

  function updateScrollEffects() {
    ticking = false;
    if (reduced.matches || mobileLayout.matches) return;

    if (hero) {
      var heroRect = hero.getBoundingClientRect();
      if (heroRect.bottom > 0 && heroRect.top < window.innerHeight) {
        var travel = Math.max(-heroRect.top, 0);
        var grid = hero.querySelector('.blueprint-grid');
        var frame = hero.querySelector('.dimension-frame');
        var drawing = hero.querySelector('.blueprint-drawing');
        if (grid) grid.style.transform = 'translate3d(0,' + (travel * 0.025) + 'px,0)';
        if (frame) frame.style.transform = 'translate3d(0,' + (travel * 0.045) + 'px,0)';
        if (drawing) drawing.style.transform = 'translate3d(0,' + (travel * 0.07) + 'px,0)';
      }
    }

    if (processRail) {
      var rect = processRail.getBoundingClientRect();
      var start = window.innerHeight * 0.78;
      var distance = Math.max(rect.height + window.innerHeight * 0.45, 1);
      var progress = Math.max(0, Math.min(1, (start - rect.top) / distance));
      processRail.style.setProperty('--process-progress', (progress * 88) + '%');
    }
  }

  function requestScrollUpdate() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(updateScrollEffects);
  }

  if (!reduced.matches && !mobileLayout.matches && (hero || processRail)) {
    window.addEventListener('scroll', requestScrollUpdate, { passive: true });
    window.addEventListener('resize', requestScrollUpdate, { passive: true });
    requestScrollUpdate();
  }

  reduced.addEventListener('change', function (event) {
    if (event.matches) {
      document.querySelectorAll('.blueprint-grid,.dimension-frame,.blueprint-drawing').forEach(function (layer) {
        layer.style.transform = '';
      });
      revealItems.forEach(show);
      blueprintStages.forEach(show);
    }
  });

  mobileLayout.addEventListener('change', function (event) {
    if (!event.matches) {
      requestScrollUpdate();
      return;
    }
    document.querySelectorAll('.blueprint-grid,.dimension-frame,.blueprint-drawing').forEach(function (layer) {
      layer.style.transform = '';
    });
  });

  window.addEventListener('load', function () {
    var connection = navigator.connection;
    if (!window.matchMedia('(prefers-reduced-motion: no-preference)').matches || window.innerWidth < 720 || (connection && connection.saveData)) return;
    var video = document.querySelector('.hero-media__video');
    if (!video) return;
    function showVideo() { video.classList.add('is-playing'); }
    video.addEventListener('canplay', showVideo, { once: true });
    var source = document.createElement('source');
    source.src = '/assets/hero.mp4';
    source.type = 'video/mp4';
    video.appendChild(source);
    video.load();
    video.play().then(showVideo).catch(function () {});
  });
})();
