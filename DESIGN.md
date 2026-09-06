# DESIGN.md — nwgeneralcontractor.com design system ("Workshop", corrected)

Version 2026-09-06. Every build, edit, and review of this site reads this file first. Silence here means
the model invents a default, so this file is not silent. Sister sites (washingtonhomesolutions.com,
waforeclosurehelp.com) have their own systems; never borrow their tokens. At a squint this site must
read as a job site and a drafting table, not as a magazine and not as a park.

## 1. Identity

- Person: a Snohomish County homeowner planning an ADU, addition, kitchen, bath, deck, or repair;
  comparing contractors; worried about permits, code, and getting ghosted. Often on a phone, often at
  the kitchen table at night.
- Pain: unlicensed bids, vague scopes, permit surprises, projects that stall.
- Promise: NW General Contractor (NW Style Homes 1 LLC, WA registration NWSTYSH768DA, bond $30,000,
  general liability $1,000,000) plans the space, writes a fixed-scope proposal with the state disclosure,
  pulls the permits, builds to Snohomish County code, and walks it through inspection.
- The one sentence the homepage installs: "These people are registered, insured, and organized, and they
  will tell me exactly what it costs and what happens next."
- Success metric: estimate requests and calls.

## 2. The world

Technical drawing. The blueprint system already built (fine grid, orange dimension frame, 17 service
line drawings that draw themselves on entry, area map pins) is honest and distinct; keep it and make it
the only imagery system. No generated photography, no "architectural concept" renders, no ambient
video. Real photos only: David's portrait (images/david-headshot.jpg, his sanctioned studio portrait)
and, when they exist, real job photos with the client's permission. Retire `assets/identity/*` (the
gpt-image-2 render, the Seedance loop, motion.css/js) and `css/identity.css` (the Georgia/copper/paper
override that pulled the site back into the cream-and-serif family).

## 3. Typography

Two families plus a mono for labels, self-hosted from `/assets/fonts/` (OFL):

| Role | Family | Files | Use |
|---|---|---|---|
| Display | Barlow Condensed | barlow-condensed-700.woff2, -800.woff2 | H1/H2 uppercase, tracking +0.01em at 2rem tightening to -0.01em at 4.5rem, line height 0.92 to 1.0 |
| Text | IBM Plex Sans | ibm-plex-sans-var.woff2 (400..600) | body 17px/1.55 (18px from 900px), measure 64ch, `text-wrap: pretty`; H3 at 600 |
| Labels | IBM Plex Mono | ibm-plex-mono-400.woff2, -500.woff2 | dimension labels, the registration number, small captions, tabular figures |

No serif anywhere. `font-display: swap`, preload the display and text files, latin unicode-range.
Hero H1 max two lines at 1440 (clamp(2.75rem, 5.2vw, 4.5rem)) and three at 390 (2.4rem).

## 4. Colour

- `--charcoal: #161616` (header, hero, footer, drawing grounds; not pure black)
- `--concrete: #e7e4dc` (page ground) · `--paper: #fbfaf7` (raised panels) · `--ink: #1c1c1c`
- `--steel: #6f7f89` (secondary text on light) · `--steel-light: #b8c1c5` (secondary text on charcoal)
- `--orange: #ff6a13` (buttons, active states, dimension lines, on charcoal) ·
  `--orange-text: #a94000` (the accent as text on light grounds, 4.5:1)
- `--bone: #f4f1ea` (type on charcoal). One accent hue (safety orange) across both grounds, two stops.
- No gradients, no gradient text, no glow. Contrast measured on the render: body 4.5:1, large 3:1.

## 5. Spacing, radius, depth

4px base scale (`--s1` 4 … `--s10` 128). Section padding `clamp(44px, 8vw, 112px)`. More space above a
heading than below. Gutter `clamp(20px, 4vw, 48px)`; content max 1200px; prose max 64ch.
Radius: 0 on panels and drawings, 2px on inputs and buttons. No pills. Depth: hairline rules
(`1px solid #cfcac0` on concrete, `#2a2a2a` on charcoal), one raised panel shadow tinted to charcoal
(`0 8px 24px rgba(22,22,22,.14)`), overlap where the estimate panel crosses the hero edge. Three
elevations, no more.

## 6. Components

- Buttons: square-cornered, Barlow Condensed 700 uppercase 1rem with +0.04em tracking, 46px min height,
  one to three words. Primary orange fill with charcoal text; secondary 1.5px outline. States: hover
  (fill darkens 8%), focus-visible (2px orange ring, 2px offset), active (translateY(1px)), disabled 55%.
- Top bar: "Registered, bonded and insured · WA contractor NWSTYSH768DA" in Plex Mono, unchanged.
- Header: logo mark + wordmark, Services, Areas, Portfolio, Blog, Contact, phone button. Mobile: the
  existing scrollable link strip and the bottom call bar (Call / Estimate).
- Services: not a card grid. A drafting index: two-column ledger rows on desktop (drawing thumbnail
  at left, service name in Barlow, one-line scope in Plex, a mono "sheet" code like `A-03` only if it
  helps scanning), one column on phones, hairlines between rows. Same schema for every row.
- Process rail: five stations with the progress line that fills; station labels in mono.
- Credentials block: facts only, mono labels: Registration NWSTYSH768DA · Bond $30,000 · General
  liability $1,000,000 · Permits handled application through inspection. Link to the disclosure page.
- Estimate form: markup, field names, ids, and `js/main.js` behaviour unchanged (ContractorMate POST,
  idempotency key, consent text). Restyle only.
- Portfolio: drawing tiles with the honest line "Real job photos are being added; call for references."

## 7. Motion

`transform`, `opacity`, `clip-path`, `stroke-dashoffset` (draw-on) only. Ease-out; UI under 220ms;
reveals 350 to 450ms once; the three hero planes at three rates on scroll (transform only); draw-on
drawings on entry; reduced motion renders everything complete and still. No autoplay video, no
scroll hijack, no scroll cues.

## 8. Browser surfaces

`::selection` orange on charcoal / charcoal on concrete; caret orange; focus ring 2px orange with
offset; thin scrollbar with a steel thumb; underline offset 3px; tabular figures everywhere numbers
appear.

## 9. Voice and copy

Plain, exact, unhurried. Name the pain first (permits, scope, schedule), then the promise, then the
proof. Real numbers only (the bond, the insurance, the registration; never invented counts or
timelines). No banned words (transform, seamless, dream, elevate, hassle-free, unleash, next-gen),
no em dashes, no exclamation marks, no "we bring your vision to life". Keep the legal footer line, the
RCW 18.27.114 disclosure page, and the JSON-LD legalName/identifier exactly.

## 10. This site does not use

Serif type; cream/paper page grounds with copper accents; AI-generated hero photos or renders; ambient
video; a centred hero with three cards; icon-grid feature sections; identical card grids; pills;
gradients; glow; emoji; eyebrows on every heading; section counters; scroll cues; testimonials that do
not exist; stock photos.
