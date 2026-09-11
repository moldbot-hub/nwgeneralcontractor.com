# Workshop Redesign Notes

## Outcome

The 48-page static site now uses the Workshop identity from `DESIGN.md`: charcoal drawing-board surfaces, concrete and paper content grounds, safety-orange construction marks, steel secondary text, square geometry, hairline rules, local trade typography, and blueprint drawings. The retired generated-identity layer is gone.

The worktree remains on `design/workshop-deslop-2026-09`. Nothing was committed, pushed, deployed, or submitted to a lead endpoint.

## What changed

- Added five local `@font-face` rules with `font-display: swap` and the Latin unicode range:
  - Barlow Condensed 700 and 800 for display type
  - IBM Plex Sans variable 400 through 600 for body type
  - IBM Plex Mono 400 and 500 for labels, dimensions, and data
- Preloaded Barlow Condensed 800 and IBM Plex Sans variable in every page head. Every local stylesheet, script, font, and active image URL now has an idempotent eight-character SHA-256 query stamp.
- Removed all serif declarations, Georgia references, gradients, glow, identity assets, video references, identity scripts, counters, scroll cues, and homepage section numbering.
- Rebuilt the shared chrome with the required top bar, desktop navigation, mobile link strip, fixed mobile call and estimate bar, and legal footer. The existing phone number, legal footer line, disclosure link, JSON-LD `legalName`, and JSON-LD identifier were preserved.
- Replaced every active hero render with the three-plane blueprint system: grid, dimension frame, and drawing on charcoal. Drawings use a short draw-on effect, while reduced-motion and sub-900 layouts render a complete static state.
- Created `assets/og-source.svg` and rendered it through local Chrome to `assets/og.png` at 1200 by 630. It uses the logo, blueprint grid, construction marks, and line drawing only. Every Open Graph and Twitter image tag points to the stamped PNG.
- Rebuilt the homepage in the required order: two-line desktop and three-line mobile H1, one-line promise, registration/bond/liability/permit proof strip, David identity strip and portrait, Call and Request an estimate actions, 17-row service drafting ledger, five-step process rail, nine-area band, credentials facts, three recent guides, estimate form, and footer.
- Kept `images/david-headshot.jpg` on the about page and added the same dimensioned image to the homepage owner strip.
- Restyled service, area, blog, about, contact, portfolio, disclosure, privacy, and 404 pages through the shared Workshop tokens and chrome. Existing secondary-page content, links, forms, article bodies, and FAQ wording remain protected by the audit.
- Replaced portfolio placeholders with blueprint drawings and the honest project-photo notice.
- Simplified `js/ui.js` to progressive reveals, blueprint draw-on, desktop-only three-rate parallax, process progress, and FAQ synchronization. `js/main.js` and `js/tracking.js` remain byte-identical.
- Added `scripts/build_site.py` for repeatable homepage composition and asset stamping. It scopes itself to the 48 production pages and is idempotent.
- Updated the test and audit baselines for the retired identity layer, drafting ledger, local fonts, cache stamps, phone counts, registration/disclosure coverage, and homepage copy rules. Production discovery is explicitly limited to root, `areas`, `blog`, and `services`, so browser tooling under `lab` cannot be mistaken for site pages.
- Added the Playwright capture helper and retained the final evidence under `lab/shots/`.

## DESIGN.md fork choices

- `DESIGN.md` requires a service drafting ledger, while `REDESIGN_SPEC.md` still describes a card grid. The homepage follows `DESIGN.md` and uses ledger rows.
- `REDESIGN_SPEC.md` contains an obsolete phone number, while the run instructions require the current number to remain unchanged. The existing `(425) 439-7700` and `tel:+14254397700` occurrences were preserved exactly, including their per-page counts.
- `DESIGN.md` requires facts-only credentials and rejects invented testimonials. The homepage testimonial material was removed, and the credential presentation contains only the registration, bond, insurance, and permit facts.
- The homepage was deliberately recomposed under the new Section 6 order. Secondary-page body copy and FAQs were preserved as required. The banned-word and visible em-dash acceptance check therefore applies to the newly authored homepage copy without rewriting protected articles or FAQ answers.

## Verification results

### Automated tests

```text
python -m unittest discover -s tests -p "test_*.py" -v
Ran 24 tests in 0.117s
OK

python tests/site_audit.py verify
VERIFY PASS: 48 HTML pages
Internal references: 2179 checked; broken=0
JSON-LD: 120 blocks parsed; valid GeneralContractor pages=48/48
Protected content: main.js, tracking.js, disclosure body, 14 blog bodies checked
Sizes: css/style.css=32491 bytes; js/ui.js=3891 bytes

node --check js/ui.js
PASS

node --check js/main.js
PASS
```

The site audit is also the repository-wide internal link checker. It resolves internal `href`, `src`, and fragment targets across all 48 production pages.

The final build-helper repeatability check found 48 production pages, `Idempotent=True`, and zero files changed by a second run.

`git diff --check` passed. Git's Windows line-ending normalization notices are informational and did not report whitespace errors.

Protected script hashes:

```text
js/main.js      5f2e694802d92004f9e1285a2af48b40ada7ed0bf64e70ea1f94fe097c54de65
js/tracking.js  7c1d71dd1967f3d70a6c56bcd970951681dde120727ad7904a82a803ea19798b
```

### Browser verification

Chrome launched from `C:\Program Files\Google\Chrome\Application\chrome.exe` through `playwright-core`. Final full-page screenshots were captured and visually inspected at 1440 by 1000 and 390 by 844 for:

- `index.html`
- `services/adu-construction.html`
- `areas/everett.html`
- `blog/adu-cost-snohomish-county.html`
- `about.html`
- `contact.html`

All 12 captures returned HTTP 200, loaded Barlow Condensed, IBM Plex Sans, and IBM Plex Mono, reported zero horizontal overflow, zero missing or dimensionless images, zero page errors, and zero failed local requests. The homepage H1 measured two lines at 1440 and three at 390. The final screenshots and the machine-readable report are in `lab/shots/`.

The sandbox denied the GA4 network request, producing the expected browser console resource error. No site asset failed, and no ContractorMate request was made.

### Asset sizes and hashes

```text
css/style.css                             32491 bytes  b10fa4cb
js/ui.js                                   3891 bytes  a3df498b
js/main.js                                10850 bytes  5f2e6948
js/tracking.js                             2949 bytes  7c1d71dd
assets/og.png                            154562 bytes  952557b6
assets/og-source.svg                       2331 bytes  6442632d
assets/fonts/barlow-condensed-700.woff2   22444 bytes  3787a5a4
assets/fonts/barlow-condensed-800.woff2   22464 bytes  2515494e
assets/fonts/ibm-plex-mono-400.woff2      14708 bytes  08949f72
assets/fonts/ibm-plex-mono-500.woff2      14888 bytes  01d28544
assets/fonts/ibm-plex-sans-var.woff2      45712 bytes  e2291e84
```

The only runtime external request declarations are the protected ContractorMate endpoint in `js/main.js` and GA4 in `js/tracking.js`. There are no external font, image, stylesheet, or video requests.

## Deleted files

```text
css/identity.css
assets/identity/hero-small.webp
assets/identity/hero.webp
assets/identity/hero.mp4
assets/identity/motion.css
assets/identity/motion.js
assets/identity/og.jpg
assets/identity/provenance.json
```

The now-empty `assets/identity/` directory was removed.

## Round 2

- Tightened the homepage hero to `clamp(48px, 7vw, 88px)` vertical padding and rendered gaps of 20px, 40px, 32px, and 32px from H1 through the actions. At 1440 the hero is 709px tall, the H1 is two lines, and the blueprint drawing is centred on the full stack; at 390 the H1 remains three lines.
- Deleted `assets/hero.mp4`, `assets/hero-poster.jpg`, `assets/hero-poster-640.jpg`, `images/hero.jpg`, `images/tree-rings.jpg`, and `images/headshot.jpg`. The runtime must-not-reference list now checks all six paths. `images/david-headshot.jpg` and the approved logo, favicon, Open Graph, and font assets remain.
- Made the homepage guides a two-plus-one drafting layout at 1440: the first guide is wide with its full excerpt, while the two linked guides at right show date and title. At 390 they collapse to one column; the secondary excerpts stay suppressed to preserve the same hierarchy without changing their source content or links.
- Locked the service ledger to a shared baseline grid. Every 1440 row is 166px with a 112 by 96 drawing; every 390 row is 142px with an 80 by 80 drawing and a 254px text column. The browser report found zero copy/drawing overlaps.
- Added and ran `scripts/stamp_assets.py`; two consecutive runs processed 48 pages and reported `Idempotent=True`.

Reference check after deletion:

```text
rg -n --glob '*.html' --glob '*.css' --glob '*.js' 'assets/hero\.mp4|assets/hero-poster\.jpg|assets/hero-poster-640\.jpg|images/hero\.jpg|images/tree-rings\.jpg|images/headshot\.jpg' .
Retired media reference check: 0 matches in HTML/CSS/JS
```

Screenshots inspected at 1440 by 1000 and 390 by 844: `index`, `service-adu-construction`, `area-everett`, `blog-adu-cost`, `about`, and `contact`. All 12 current captures are in `lab/shots/`; `report.json` contains 12 results and the capture runner reported zero mechanical failures.

## Open items

- No real estimate form was submitted. This avoided transmitting a test lead or spending service credits.
- No deployed Lighthouse run was performed because this run was explicitly local and unpushed. CSS and UI JavaScript are within the requested budgets, active images have dimensions and below-fold lazy loading, and the browser pass found no layout overflow.
- The sandbox blocked recursive cleanup of Chrome's ignored scratch directory at `lab/tmp/`. It is excluded in `.gitignore` and is not part of the site or screenshot deliverables.
- The branch and linked worktree were intentionally left as-is with no commit or push.
