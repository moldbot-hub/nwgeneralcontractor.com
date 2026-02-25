/* ==========================================================================
   SetMate Visitor Tracking — Captures referrer, UTM, and page visits
   ========================================================================== */
(function() {
  var STORAGE_PREFIX = '_sm_';

  function getItem(key) {
    try { return JSON.parse(localStorage.getItem(STORAGE_PREFIX + key)); } catch(e) { return null; }
  }
  function setItem(key, val) {
    try { localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(val)); } catch(e) {}
  }

  // Generate visitor ID (once per browser)
  if (!getItem('vid')) {
    setItem('vid', 'v_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36));
  }

  // First touch — referrer + landing page (only set once)
  if (!getItem('referrer') && document.referrer) {
    // Only store external referrers (not same-site navigation)
    try {
      var ref = new URL(document.referrer);
      if (ref.hostname !== location.hostname) {
        setItem('referrer', document.referrer);
      }
    } catch(e) {}
  }
  if (!getItem('landing')) {
    setItem('landing', location.pathname + location.search);
  }

  // UTM parameters (capture once, first visit with UTMs wins)
  if (!getItem('utm')) {
    var params = new URLSearchParams(location.search);
    var utm = {};
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'].forEach(function(key) {
      var val = params.get(key);
      if (val) utm[key.replace('utm_', '')] = val;
    });
    if (Object.keys(utm).length > 0) {
      setItem('utm', utm);
    }
  }

  // Track page visit
  var pages = getItem('pages') || [];
  pages.push({
    url: location.pathname,
    title: document.title.split('|')[0].trim(),
    ts: new Date().toISOString()
  });
  // Cap at 50 entries
  if (pages.length > 50) pages = pages.slice(-50);
  setItem('pages', pages);

  // Public API for form submission
  window._smTracking = {
    getData: function() {
      return {
        visitorId: getItem('vid'),
        referrer: getItem('referrer') || null,
        landingPage: getItem('landing') || null,
        utm: getItem('utm') || null,
        pagesVisited: getItem('pages') || []
      };
    },
    clear: function() {
      ['vid', 'referrer', 'landing', 'utm', 'pages'].forEach(function(key) {
        try { localStorage.removeItem(STORAGE_PREFIX + key); } catch(e) {}
      });
    }
  };
})();
