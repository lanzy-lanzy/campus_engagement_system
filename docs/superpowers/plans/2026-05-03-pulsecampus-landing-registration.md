# PulseCampus Landing and Registration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Campus Voice with PulseCampus and ship a modern public landing page plus redesigned registration page with a Three.js visual scene.

**Architecture:** Anonymous users see a public landing page from `posts.views.feed`; authenticated users keep the existing feed. Shared PulseCampus branding lives in templates, CSS, and JS so auth, landing, and nav remain consistent without changing models or form behavior.

**Tech Stack:** Django templates, Django TestCase, Tailwind CDN, Alpine.js, HTMX, Three.js CDN, plain JavaScript.

---

### Task 1: Brand and Landing Tests

**Files:**
- Modify: `posts/tests.py`
- Modify: `accounts/tests.py`

- [ ] Add tests that assert anonymous `posts:feed` renders PulseCampus landing content, not the feed composer.
- [ ] Add tests that assert authenticated `posts:feed` still renders the feed.
- [ ] Add tests that assert register renders PulseCampus branding, tagline, and the Three.js canvas mount.
- [ ] Run: `python manage.py test posts.tests.PostViewTests.test_anonymous_feed_renders_pulsecampus_landing accounts.tests.AuthFlowTests.test_register_renders_pulsecampus_branding`
- [ ] Expected: tests fail because landing/register branding is not implemented yet.

### Task 2: Landing Route and Template

**Files:**
- Modify: `posts/views.py`
- Create: `templates/landing.html`
- Modify: `templates/base_auth.html`

- [ ] Update `posts.views.feed` so anonymous users render `landing.html`.
- [ ] Create `landing.html` with PulseCampus logo, tagline, CTA buttons, product stats, feature section, and `<div data-pulse-scene>`.
- [ ] Update `base_auth.html` title and metadata to PulseCampus and include a Three.js CDN script before `static/js/app.js`.
- [ ] Run the failing landing test and confirm it passes.

### Task 3: Registration Redesign

**Files:**
- Modify: `templates/accounts/register.html`
- Modify: `templates/accounts/login.html`

- [ ] Replace old auth card with a modern PulseCampus onboarding panel.
- [ ] Preserve `{% csrf_token %}`, all Django fields, help text, and error rendering.
- [ ] Add the tagline and `<div data-pulse-scene data-scene-variant="auth">`.
- [ ] Update login text and CTA labels to PulseCampus.
- [ ] Run the register branding test and confirm it passes.

### Task 4: Visual System and Three.js Scene

**Files:**
- Modify: `static/css/app.css`
- Modify: `static/js/app.js`

- [ ] Add PulseCampus CSS for logo marks, landing shell, auth layout, cards, responsive canvas sizing, and reduced-motion handling.
- [ ] Add a guarded `initPulseScene()` function that only runs when `[data-pulse-scene]` exists and `window.THREE` is available.
- [ ] Render a nonblank scene: connected campus nodes, floating post cards, pulse rings, and subtle rotation.
- [ ] Keep all existing mention/HTMX JavaScript behavior intact.

### Task 5: App-Wide Brand Replacement

**Files:**
- Modify: `templates/base.html`
- Modify: `templates/partials/topnav.html`
- Modify: any template/static file containing user-facing `Campus Voice` or `CampusVoice`

- [ ] Replace user-facing Campus Voice references with PulseCampus.
- [ ] Preserve route names and existing app behavior.
- [ ] Run a text search to confirm no user-facing old brand remains outside historical docs.

### Task 6: Verification

**Files:**
- Test command only.

- [ ] Run: `python manage.py test accounts.tests posts.tests`
- [ ] Run: `python manage.py runserver 127.0.0.1:8000`
- [ ] Use browser automation or Playwright to capture desktop and mobile screenshots for `/` and `/accounts/register/`.
- [ ] Confirm the canvas has nonblank pixels and does not overlap registration controls.
