# Workshop Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild all 48 existing static pages in the approved charcoal, concrete, and safety-orange Workshop identity while preserving URLs, page content, structured data, legal facts, links, and lead-capture behavior.

**Architecture:** Keep the site dependency-free and static. A repository audit script captures the pre-redesign page-specific content and validates the finished HTML; a one-time deterministic migration script applies shared header, footer, hero, and page-type markup while leaving article and long-form content blocks intact. Presentation lives in one stylesheet and motion in one small progressive-enhancement script.

**Tech Stack:** HTML5, CSS3, inline SVG, vanilla JavaScript, Python 3 standard library verification.

**Spec:** `REDESIGN_SPEC.md`

## Global Constraints

- Work in place on `redesign/workshop-2026-09`; do not create a worktree, commit, push, deploy, or use network resources.
- Preserve all 48 URLs, page-specific factual content, FAQs, JSON-LD facts, form contracts, telephone number, registration identifier, disclosure content, and internal links.
- Keep `js/main.js` and `js/tracking.js` byte-for-byte unchanged.
- Use only local assets and system font stacks.
- Keep `css/style.css` below 45 KB and `js/ui.js` below 8 KB.
- Remove the 17 service hero JPGs only after HTML and CSS contain no references to them.
- Use no subagents; the controlling instruction for this session prohibits delegation unless the user requests it.

---

### Task 1: Capture the Baseline and Establish Failing Acceptance Tests

**Files:**
- Create: `tests/site_audit.py`
- Create: `tests/baseline-content.json`

**Interfaces:**
- Produces: `python tests/site_audit.py capture` and `python tests/site_audit.py verify`.
- The baseline records each page's structured-data objects, page-specific content text, internal link targets, forms, and script selectors while excluding replaceable global chrome.

- [ ] **Step 1: Implement baseline capture and acceptance assertions**

  The verifier must report page count, broken internal references, JSON-LD parse errors, GeneralContractor/provider identity errors, legal-line omissions, forbidden names, `main.js` selector coverage, article-body drift, missing baseline content/links/forms, external asset dependencies, image dimensions/lazy-loading, required Workshop structures, and size limits.

- [ ] **Step 2: Capture the untouched repository**

  Run: `python tests/site_audit.py capture`

  Expected: `tests/baseline-content.json` contains 48 page records and SHA-256 hashes for `js/main.js`, `js/tracking.js`, the disclosure body, and every blog article body.

- [ ] **Step 3: Run the acceptance suite before implementation**

  Run: `python tests/site_audit.py verify`

  Expected: FAIL specifically because Workshop heroes, SVG drawings, `js/ui.js`, homepage ordering, and the final legal/header normalization do not yet exist.

### Task 2: Build Shared Workshop Presentation and SVG Primitives

**Files:**
- Replace: `css/style.css`
- Create: `js/ui.js`
- Create: `tools/workshop_migrate.py`

**Interfaces:**
- `tools/workshop_migrate.py` reads the 48 HTML files and emits deterministic header/footer and page-type markup.
- Inline SVGs expose `.blueprint-grid`, `.dimension-frame`, `.blueprint-drawing`, and `.blueprint-stroke` for CSS and `js/ui.js`.

- [ ] **Step 1: Add shared header/footer, blueprint, and page-type migration fixtures to the acceptance suite**

  Run: `python tests/site_audit.py verify`

  Expected: FAIL with missing Workshop classes and missing `js/ui.js`.

- [ ] **Step 2: Implement the single Workshop stylesheet**

  Include exact palette variables, condensed uppercase display stack, 17px/1.55 body typography, sticky charcoal header, scrollable mobile navigation, service/content/sidebar layouts, details/summary styling, cards, process rail, area chips, badge block, forms, footer, mobile call bar, reveal states, and reduced-motion rules.

- [ ] **Step 3: Implement progressive enhancement in `js/ui.js`**

  Add IntersectionObserver reveal/drawing behavior, requestAnimationFrame transform-only hero parallax, process-line progress, optional counters, FAQ details synchronization, and immediate complete rendering when reduced motion is requested or APIs are unavailable.

- [ ] **Step 4: Verify script syntax and budgets**

  Run: `node --check js/ui.js`

  Expected: PASS, with `js/ui.js` under 8 KB and `css/style.css` under 45 KB.

### Task 3: Migrate Shared Chrome and Page Types

**Files:**
- Modify: all 48 `*.html` files

**Interfaces:**
- Every page receives the same legal top bar, primary link strip, footer legal line, mobile call bar, `tracking.js`, `main.js`, and `ui.js`, using root-relative URLs.
- Service pages receive their matching service drawing and two-column sticky-estimate structure.
- Area pages receive a map-pin blueprint block and two-column structure.
- Blog articles keep their body subtree unchanged.

- [ ] **Step 1: Run the deterministic migration**

  Run: `python tools/workshop_migrate.py`

  Expected: all 48 HTML pages receive Workshop chrome, page-type body classes, appropriate hero treatment, and script references.

- [ ] **Step 2: Convert service FAQs to accessible details/summary without changing question or answer text**

  Run: `python tests/site_audit.py verify`

  Expected: any remaining failures identify specific page-level omissions rather than content drift.

- [ ] **Step 3: Fix page-specific migration exceptions**

  Apply only targeted changes for malformed or uniquely structured pages, preserving baseline content and links.

### Task 4: Recompose the Homepage and Honest Portfolio

**Files:**
- Modify: `index.html`
- Modify: `portfolio.html`

**Interfaces:**
- `index.html` section order is hero, 17-service grid, process rail, nine-area band, credentials block, recent guides, estimate form, footer.
- `portfolio.html` uses drawing tiles and the exact statement `Real job photos are being added; call for references`.

- [ ] **Step 1: Rebuild the homepage around the approved ADU-led message**

  Use the exact H1 and promise facts, 17 linked service drawing cards, five process steps including the state disclosure link, nine area chips, bond/insurance/registration facts, existing blog guide links, and a compatible estimate form.

- [ ] **Step 2: Replace portfolio placeholder imagery with blueprint drawing tiles**

  Preserve existing portfolio explanatory content and links while adding the required honest availability statement.

- [ ] **Step 3: Run content and structure verification**

  Run: `python tests/site_audit.py verify`

  Expected: PASS except for intentionally pending asset deletion and browser checks.

### Task 5: Remove Obsolete Hero Assets and Document the Redesign

**Files:**
- Delete: `images/adu-hero.jpg`, `images/bathroom-hero.jpg`, `images/carpentry-hero.jpg`, `images/deck-hero.jpg`, `images/fencing-hero.jpg`, `images/flooring-hero.jpg`, `images/foundation-hero.jpg`, `images/garage-hero.jpg`, `images/home-additions-hero.jpg`, `images/kitchen-hero.jpg`, `images/outdoor-living-hero.jpg`, `images/painting-hero.jpg`, `images/patio-hero.jpg`, `images/roofing-hero.jpg`, `images/siding-hero.jpg`, `images/whole-home-hero.jpg`, `images/windows-hero.jpg`
- Create: `REDESIGN_NOTES.md`

**Interfaces:**
- `REDESIGN_NOTES.md` summarizes changes, browser checks, verification commands, and open items.

- [ ] **Step 1: Prove the 17 JPGs have zero source references**

  Run: `rg -n "(adu|bathroom|carpentry|deck|fencing|flooring|foundation|garage|home-additions|kitchen|outdoor-living|painting|patio|roofing|siding|whole-home|windows)-hero\\.jpg" -g "*.html" -g "*.css" -g "*.js"`

  Expected: no output.

- [ ] **Step 2: Delete exactly the 17 obsolete hero JPGs**

  Resolve and validate each path inside the repository `images` directory before removing it.

- [ ] **Step 3: Write redesign notes**

  Record the design system, page-type changes, behavior preservation, local browser checklist, and any remaining limitations.

### Task 6: Fresh Final Verification and Handoff

**Files:**
- Verify: all changed files

**Interfaces:**
- Produces the evidence requested in `REDESIGN_SPEC.md` for the final response.

- [ ] **Step 1: Run the complete repository audit**

  Run: `python tests/site_audit.py verify`

  Expected: PASS with 48 pages, zero broken links, zero JSON-LD errors, zero legal/identity errors, selector coverage confirmed, no content drift, and no obsolete hero references.

- [ ] **Step 2: Run independent grep and syntax checks**

  Run: `node --check js/main.js; node --check js/tracking.js; node --check js/ui.js`

  Expected: all exit 0.

- [ ] **Step 3: Serve and inspect representative routes locally**

  Start a Python static server and inspect the homepage, one service, one area, one blog article, contact, portfolio, and disclosure at desktop and mobile widths. Confirm no console errors, horizontal overflow, inaccessible controls, broken drawings, or form-selector regressions.

- [ ] **Step 4: Print final sizes, retained images, selectors, and changed-file list**

  Run read-only filesystem and Git commands so the final response contains fresh output rather than inferred results.

