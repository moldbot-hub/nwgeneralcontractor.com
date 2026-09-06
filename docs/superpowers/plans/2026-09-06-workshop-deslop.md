# Workshop De-slop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore all 48 static routes to the approved Workshop identity, remove the retired AI-generated identity layer, self-host the supplied fonts, and prove the result mechanically and visually.

**Architecture:** Keep the existing dependency-free HTML, shared stylesheet, inline blueprint SVGs, protected lead-capture JavaScript, and protected analytics JavaScript. Extend the Python audit as the acceptance boundary, use one idempotent stamping helper for site-wide hashed asset URLs, and keep all presentation in `css/style.css` plus progressive enhancement in `js/ui.js`.

**Tech Stack:** Static HTML5, CSS3, inline SVG, vanilla JavaScript, Python 3 standard library, Pillow for image validation, Playwright Core with local Chrome for browser verification.

**Spec:** `DESIGN.md` and `REDESIGN_SPEC.md`

## Global Constraints

- Do not commit, push, deploy, change any route URL, or use generated/stock imagery.
- Do not modify `js/main.js` or `js/tracking.js`; preserve their baseline hashes.
- Preserve every existing phone occurrence count per HTML page, the exact legal footer line, disclosure link, RCW disclosure body, JSON-LD facts, service/area content, blog bodies, FAQs, and internal links.
- Use `#161616`, `#e7e4dc`, `#fbfaf7`, `#ff6a13`, `#a94000`, `#6f7f89`, `#b8c1c5`, and the spacing/radius/depth rules from `DESIGN.md`.
- Keep `css/style.css` under 45 KB and `js/ui.js` under 8 KB.
- Every local stylesheet, script, and font URL must end in `?v=` plus the first eight characters of that file's SHA-256 hash.
- Treat the supplied blueprint SVG drawings as authored technical diagrams, not generated imagery.
- Because this run is unattended, record all fork choices in `REDESIGN_NOTES.md`; use read-only diff checkpoints instead of commits.

---

### Task 1: Establish the New Acceptance Boundary

**Files:**
- Modify: `tests/site_audit.py`
- Replace: `tests/test_hero_media.py`
- Modify: `tests/test_site_audit.py`
- Modify: `tests/test_workshop_regressions.py`

**Interfaces:**
- Consumes: all 48 HTML files, CSS/JS/font/social assets, and `tests/baseline-content.json`.
- Produces: precise failures for retired identity references, font roles and files, eight-character content hashes, protected phone counts, Workshop homepage structures, social metadata, serif/banned visual patterns, and image loading/dimensions.

- [ ] **Step 1: Add failing structural tests**

  Add parser-backed assertions that all pages preload `/assets/fonts/barlow-condensed-800.woff2` and `/assets/fonts/ibm-plex-sans-var.woff2`, reference only hashed local styles/scripts, point Open Graph and Twitter images at `/assets/og.png`, include registration and disclosure chrome, and contain no `/assets/identity` reference.

- [ ] **Step 2: Add failing CSS and homepage tests**

  Assert the five font faces and exact new tokens exist, CSS contains no `serif`, homepage uses 17 `.service-ledger__row` entries, contains `.hero-identity`, has no testimonial block/counter labels/scroll cue, and its visible text contains no em dash or DESIGN banned word.

- [ ] **Step 3: Prove RED**

  Run: `python -m unittest discover -s tests -p "test_*.py" -v`

  Expected: failures name the current identity assets, serif override, old tokens, missing fonts/preloads/hashes/social card, card grid, media video behavior, and homepage copy.

### Task 2: Build the Workshop Foundation

**Files:**
- Replace: `css/style.css`
- Modify: `js/ui.js`
- Create: `scripts/stamp_assets.py`
- Create: `assets/og.png`

**Interfaces:**
- `scripts/stamp_assets.py` computes SHA-256 digests for existing CSS, JS, fonts, favicon, PNG/JPG assets referenced by HTML, replaces only an existing `?v=<hex>` suffix or appends one, and produces byte-identical output on a second run.
- `css/style.css` owns typography, tokens, shared chrome, page layouts, ledger, blueprint planes, motion, forms, footer, and responsive rules.
- `js/ui.js` owns only one-shot reveal/draw behavior, desktop transform-only hero parallax, process progress, and FAQ synchronization.

- [ ] **Step 1: Implement the shared font and token layer**

  Define Barlow Condensed 700/800, IBM Plex Sans variable 400..600, and IBM Plex Mono 400/500 with `font-display:swap` and `U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+FEFF,U+FFFD`; apply display/text/label roles and exact Workshop tokens.

- [ ] **Step 2: Replace card-oriented presentation**

  Style the homepage service index as two-column ledger rows, the five-station process rail, hard-edged facts/areas/guides/form sections, and all shared page types with zero/2px radii and hairline rules.

- [ ] **Step 3: Remove media-only UI behavior**

  Delete video-loading code and counters from `js/ui.js`; retain under-450ms reveal/draw motion, reduced-motion completion, desktop-only three-plane parallax, process fill, and FAQ details synchronization.

- [ ] **Step 4: Create and verify the social card**

  Render a 1200x630 PNG using the supplied logo, charcoal ground, blueprint grid/dimension geometry, and Workshop type; assert its dimensions in tests.

### Task 3: Recompose the Homepage and Shared Metadata

**Files:**
- Modify: `index.html`
- Modify: all other 47 HTML files through `scripts/stamp_assets.py`

**Interfaces:**
- Homepage order: hero, service drafting index, process rail, areas band, credential facts, recent guides, estimate form, footer.
- Homepage hero: two-line desktop H1, one-line promise, proof strip, David identity strip with 600x750 portrait and unchanged phone, two buttons, and right-side three-plane blueprint drawing.
- Every page head: hashed stylesheet, two hashed font preloads, favicon, `/assets/og.png` Open Graph and Twitter image metadata.

- [ ] **Step 1: Replace the homepage identity/photo/video composition**

  Remove `nwgc-cover`, `identity-motion`, testimonial content, generic feature grid, counters, repeated eyebrows, and banned copy while preserving facts and links.

- [ ] **Step 2: Convert 17 service entries to ledger rows**

  Retain each service link, name, one-line scope, and SVG drawing; use stable A-series sheet labels without section counters.

- [ ] **Step 3: Update every head and script URL mechanically**

  Remove identity links/scripts, add both font preloads, add social metadata, normalize root-relative asset URLs, and stamp exact eight-character hashes.

- [ ] **Step 4: Prove stamping idempotence**

  Hash all 48 HTML files, run `python scripts/stamp_assets.py` again, and assert the HTML hashes are unchanged.

### Task 4: Retire Identity Assets and Align Representative Pages

**Files:**
- Delete: `css/identity.css`
- Delete: `assets/identity/hero-small.webp`
- Delete: `assets/identity/hero.webp`
- Delete: `assets/identity/hero.mp4`
- Delete: `assets/identity/motion.css`
- Delete: `assets/identity/motion.js`
- Delete: `assets/identity/og.jpg`
- Delete: `assets/identity/provenance.json`
- Modify: `portfolio.html`
- Modify: `about.html`
- Modify: `contact.html`

**Interfaces:**
- Shared CSS must make all service, area, blog, about, contact, portfolio, disclosure, privacy, and 404 routes use the same Workshop chrome without altering their protected bodies or link sets.

- [ ] **Step 1: Remove the exact retired files after zero-reference proof**

  Run `rg -n "/assets/identity|css/identity" -g "*.html" -g "*.css" -g "*.js"`; require no output, validate every target resolves inside this worktree, then delete only the listed files.

- [ ] **Step 2: Remove remaining visual slop in representative utility pages**

  Make David's about portrait square-cornered through markup/shared CSS, replace the portfolio's generic image-placeholder icons with existing blueprint drawings, and rely on shared form/page styles for contact.

- [ ] **Step 3: Run the focused acceptance suite**

  Run: `python -m unittest discover -s tests -p "test_*.py" -v`

  Expected: all tests pass before browser work.

### Task 5: Verify Every Required Surface

**Files:**
- Create: `lab/shots/*.png`
- Replace top section: `REDESIGN_NOTES.md`

**Interfaces:**
- The link checker validates every internal `href` and `src`, including query strings and fragments.
- Browser runner serves this root at port 4611 and captures 1440 and 390 widths for the six requested route types with local Chrome.

- [ ] **Step 1: Run required mechanical verification**

  Run the full unittest command, `python tests/site_audit.py verify`, `node --check js/ui.js`, and `node --check js/main.js`; run the independent link checker and asset/phone/protected-hash reports.

- [ ] **Step 2: Capture all 12 screenshots**

  Set `TEMP` and `TMP` to `$PWD/lab/tmp`, launch `C:\Program Files\Google\Chrome\Application\chrome.exe` through Playwright Core, serve with `python -m http.server 4611`, and save desktop/mobile captures for index, one service, one area, one blog post, about, and contact.

- [ ] **Step 3: Inspect every screenshot and repair regressions**

  Check overflow, clipped headlines, empty reveal content, contrast, image distortion, mobile sticky-bar overlap, section rhythm, and desktop grid alignment. For each repair, first add or identify the acceptance check that would fail, then rerun the relevant test and all 12 captures.

- [ ] **Step 4: Record fresh evidence**

  Replace the top section of `REDESIGN_NOTES.md` with changed/deleted files, fork choices, exact test/link/syntax/browser outputs, byte sizes for CSS/JS/fonts, protected file hashes, screenshot paths, and open items. Print that file verbatim as the final response.
