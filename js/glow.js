/* ==========================================================================
   Glowing Effect — vanilla JS port of Aceternity's GlowingEffect
   Mouse-tracking animated border glow for service cards
   ========================================================================== */

(function() {
  'use strict';

  var SPREAD = 40;
  var PROXIMITY = 64;
  var INACTIVE_ZONE = 0.01;
  var BORDER_WIDTH = 3;
  var MOVEMENT_DURATION = 2000; // ms

  function initGlow() {
    var cards = document.querySelectorAll('.glow-card');
    if (!cards.length) return;

    document.body.addEventListener('pointermove', function(e) {
      for (var i = 0; i < cards.length; i++) {
        updateCard(cards[i], e.clientX, e.clientY);
      }
    }, { passive: true });

    window.addEventListener('scroll', function() {
      for (var i = 0; i < cards.length; i++) {
        updateCard(cards[i], null, null);
      }
    }, { passive: true });
  }

  function updateCard(card, mouseX, mouseY) {
    var glowEl = card.querySelector('.glow-border');
    if (!glowEl) return;

    var rect = card.getBoundingClientRect();
    var cx = rect.left + rect.width * 0.5;
    var cy = rect.top + rect.height * 0.5;

    // Use stored position if no mouse coords (scroll event)
    if (mouseX === null) {
      mouseX = parseFloat(glowEl.getAttribute('data-mx')) || 0;
      mouseY = parseFloat(glowEl.getAttribute('data-my')) || 0;
    } else {
      glowEl.setAttribute('data-mx', mouseX);
      glowEl.setAttribute('data-my', mouseY);
    }

    var isActive =
      mouseX > rect.left - PROXIMITY &&
      mouseX < rect.left + rect.width + PROXIMITY &&
      mouseY > rect.top - PROXIMITY &&
      mouseY < rect.top + rect.height + PROXIMITY;

    if (!isActive) {
      glowEl.style.opacity = '0';
      return;
    }

    glowEl.style.opacity = '1';

    // Calculate angle from center to mouse
    var angle = Math.atan2(mouseY - cy, mouseX - cx) * (180 / Math.PI) + 90;
    glowEl.style.setProperty('--glow-start', angle + 'deg');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGlow);
  } else {
    initGlow();
  }
})();
