# PulseCampus Landing and Registration Redesign

## Goal
Replace the existing Campus Voice identity everywhere with PulseCampus and give the app a modern public entry experience. The new tagline is: "Turn student voices into campus action."

## Brand
PulseCampus should feel active, trusted, student-centered, and action-oriented. The logo mark is a compact circular symbol combining a speech bubble and pulse line, using royal blue, cyan, mint, and a small warm coral accent. Text references to Campus Voice become PulseCampus across page titles, metadata, navigation, auth pages, and comments in front-end assets.

## Landing Page
Anonymous visitors should see a full first-screen landing page rather than the authenticated feed. The page includes a top navigation, hero message, clear login/register actions, a few live-product signals, and a hint of the next section. The visual centerpiece is a full-bleed Three.js scene with floating post cards, reaction nodes, and connecting lines that suggest campus ideas becoming action.

Authenticated users continue to land on the feed through the existing post-login flow.

## Registration
The registration page keeps the existing Django form and backend behavior, but presents it as a polished onboarding flow. The layout pairs a compact registration panel with the PulseCampus visual system, includes clearer field labels and help text, and preserves all validation errors. The form remains mobile-first and does not add extra required data.

## Implementation Boundaries
Use Django templates, Tailwind CDN, Alpine.js, HTMX, and plain JavaScript. Add Three.js through a CDN script on the public/auth pages that need it. Keep changes scoped to templates, static CSS/JS, URL/view routing, and tests for anonymous landing behavior and brand rendering.

## Verification
Run Django tests for affected views and forms, then run the local server and visually check desktop and mobile landing/register pages. Confirm the Three.js canvas is nonblank, responsive, and does not overlap registration controls.
