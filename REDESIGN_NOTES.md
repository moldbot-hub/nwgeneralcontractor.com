# Workshop Redesign Notes

## What changed

- Rebuilt all 48 existing HTML routes in place around a charcoal, concrete, paper-white, safety-orange, and steel Workshop design system.
- Replaced the site-wide header and footer with a sticky charcoal navigation system, exact registration top bar, complete service/area link sets, the required legal line, and a two-action mobile call bar.
- Reworked the homepage into the required order: ADU-led hero, 17-service drawing grid, five-step process rail, nine-area band, registration/bond/insurance facts, recent guides, and estimate form.
- Added three-plane SVG blueprint heroes: a 12 px minor / 96 px major grid, orange dimension frame, and 17 distinct service drawings. Area pages use a map-pin drawing.
- Reworked service and area templates into content plus sticky-estimate layouts on desktop, stacked layouts on mobile, and converted service FAQs to native `details` / `summary` elements without changing their wording.
- Kept blog article-body markup unchanged and restyled it only through the shared chrome and stylesheet.
- Replaced the portfolio placeholders with blueprint drawing tiles and the statement: “Real job photos are being added; call for references.”
- Added `js/ui.js` for 400 ms reveal motion, blueprint draw-on, three-rate transform-only hero parallax, process progress, credential counters, and FAQ synchronization. Reduced-motion users receive the completed static state.
- Kept `js/main.js` and `js/tracking.js` byte-for-byte unchanged, including ContractorMate submission, API/idempotency headers, consent behavior, and GA4 `G-22KRBSFPDX`.
- Captured the pre-redesign content/structured-data/form baseline in `tests/baseline-content.json` and added repeatable local verification in `tests/site_audit.py`.
- Deleted exactly the 17 named service hero JPGs after a zero-reference check.
- Fixed the mobile stacked-flow regression at all widths below 900 px: sections and layout wrappers now have automatic height with no minimum or maximum reservation, sticky estimates become static, mobile reveals render visibly, and hero parallax is disabled.
- Put the desktop header tagline on its own line and hide it below 1100 px.
- Made SVG drawing captions filled 9 px monospace text with no inherited stroke or paint-order effect.
- Added the WCAG-AA light-ground text accent `#a94000`; safety orange remains the button, rule, dark-ground, and blueprint-line accent. Corrected the dark service-area paragraph color as well.
- Replaced visible footer `h4` elements with plain strong labels while retaining hidden compatibility targets for the unchanged `main.js` selector.
- Added a self-contained 32 x 32 `favicon.ico`, generated from `images/logo-sm.png`, and linked it from all 48 page heads.

## Local verification

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python tests/site_audit.py verify
node --check js/main.js
node --check js/tracking.js
node --check js/ui.js
```

The audit checks the 48-URL set, internal `href`/`src` resolution and fragments, JSON-LD parsing and contractor identity, exact legal/header wording, prohibited business names, baseline page text and internal links, form fields, protected script hashes, disclosure and blog-body hashes, SVG/page-type structures, image attributes, obsolete hero references, and CSS/JS size budgets.

## Browser checklist

- At desktop width, confirm the sticky charcoal header, service/area dropdowns, ADU-led hero composition, SVG stroke animation, and distinct parallax rates for grid/frame/drawing.
- Scroll the homepage through all sections and confirm the service reveals, five-step orange process fill, nine area chips, credential counters, guides, and estimate anchor.
- At 720 px and below, confirm the single-row horizontal navigation strip, stacked content/sidebar layouts, and fixed Call / Estimate bottom bar without horizontal page overflow.
- At 899 px and below, confirm sections use normal document flow with no reserved-height gaps and no parallax transforms; below-fold reveal items intentionally render visible in this static mobile layout.
- On a service page, open several FAQ summaries and confirm only one stays open; confirm the estimate sidebar remains sticky on desktop.
- On an area page, confirm the map-pin blueprint and local content/sidebar layout.
- Confirm blog article bodies remain readable and unchanged, the contact form retains all fields and SMS consent, the portfolio shows drawing tiles rather than photos, and the disclosure content is complete.
- If testing the form endpoint intentionally, use a controlled test lead and confirm success/error UI, `x-api-key`, and `idempotency-key` behavior without creating duplicate opportunities.
- Run a mobile Lighthouse audit and confirm the requested score of 90 or better under the deployment’s normal analytics/network conditions.

## Open items

- A local Playwright/Chromium check now covers the exact 390 x 844 viewport. It measured a zero-pixel hero-to-services gap, zero-pixel maximum gap between adjacent home sections, visible service cards, `min-height: 0`, `max-height: none`, and a static service-page estimate sidebar. A deployed Lighthouse run remains a final manual check because analytics and deployment conditions are outside this local-only pass.
- No real ContractorMate form submission was made because verification was required to remain local and must not spend API credits or transmit test lead data.
- `images/hero.jpg`, `images/headshot.jpg`, and `images/tree-rings.jpg` remain as unreferenced legacy files. They were not among the 17 files explicitly authorized for deletion. The active HTML uses only `logo-sm.png` and `david-headshot.jpg`; `logo.png` remains retained as requested.
- `git diff --check` passes. Git prints Windows line-ending normalization notices for the migrated HTML/CSS files; they are informational and do not indicate whitespace errors.
