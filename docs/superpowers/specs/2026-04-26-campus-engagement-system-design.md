# Campus Engagement System Design

## Summary

Build a web-based student feedback and engagement system as a phased Django application. The work proceeds in this order:

1. Phase 1: complete MVP with student and admin workflows.
2. Phase 2: full README feature expansion.
3. Phase 3: UI/UX polish pass.

The system uses Django Templates only, Tailwind CSS CDN, HTMX for partial updates, and Alpine.js for small interface state. It does not use React, Vue, or another frontend framework.

## Existing Project Context

The repository currently contains a minimal Django 4.2 project:

- `campus_engagement_system/`: project settings and root URLs.
- `core/`: empty starter app with only a `home` route reference.
- `templates/`, `static/`, `media/`: present but currently empty.
- `db.sqlite3`: existing development database.

The README requires a modular architecture with `accounts`, `posts`, `interactions`, and `dashboard`. Phase 1 should replace the empty starter shape with those focused apps instead of growing all behavior inside `core`.

The workspace is not currently a git repository, so design documentation can be written but cannot be committed until git is initialized.

## Goals

Phase 1 must produce a working MVP:

- Student registration, login, logout, and role-aware redirection.
- Custom user model ready for student/admin roles.
- Student feed with latest, most liked, and trending sort choices.
- Create, edit, and delete own posts.
- Post categories: Suggestion, Complaint, Improvement, Event Idea.
- Optional post image upload.
- Like and heart reactions without full page reloads.
- Threaded comments added dynamically with HTMX.
- Report inappropriate posts or comments.
- Student profile with posts and activity summary.
- Admin dashboard with totals, active students, reported content, and engagement metrics.
- Admin moderation for posts, comments, and reports.
- Mobile-first sidebar dashboard layout.

Phase 2 expands the full README scope:

- Search and category/status filters.
- More explicit trending scoring.
- Tags or hashtag-ready post metadata.
- Notification-ready structure using HTMX polling patterns.
- Richer analytics for admin review.
- PostgreSQL-ready environment configuration.
- Email-verification-ready account flow without requiring live email delivery in development.

Phase 3 refines the UI/UX:

- Responsive sidebar behavior on mobile and desktop.
- Polished modal create/edit post forms.
- Clear empty states, loading states, validation states, and HTMX swap states.
- Feed cards optimized for scanning and repeated engagement.
- Admin dashboard tuned for dense operational review.

## Non-Goals

- Do not add React, Vue, or a frontend build system.
- Do not require external services for the MVP.
- Do not implement real-time WebSockets in Phase 1.
- Do not overbuild notifications before the core engagement loops work.
- Do not retain `core` as the main feature app once modular apps exist.

## Architecture

Use four domain apps:

- `accounts`: custom `User`, authentication views/forms, role helpers, profile views.
- `posts`: `Post`, feed/list/detail behavior, post create/edit/delete, image uploads.
- `interactions`: `Reaction`, `Comment`, `Report`, HTMX endpoints for reactions, comments, reporting, and dynamic deletes.
- `dashboard`: admin-facing dashboards, moderation queues, report review, analytics summaries.

Root project responsibilities stay in `campus_engagement_system/`:

- Settings, installed apps, static/media configuration, auth model configuration, and root URL inclusion.
- Development SQLite defaults.
- PostgreSQL-ready database configuration can be introduced in Phase 2 through environment variables.

Templates should be organized by app and shared partials:

- `templates/base.html`: document shell, Tailwind CDN, HTMX, Alpine.js, sidebar layout.
- `templates/accounts/`: auth and profile pages.
- `templates/posts/`: feed, post cards, post forms.
- `templates/interactions/partials/`: reaction counters, comment threads, report confirmations.
- `templates/dashboard/`: admin dashboard and moderation pages.
- `templates/partials/`: shared navigation, messages, pagination, modal shell.

Static assets remain light:

- Tailwind CSS comes from CDN.
- Custom CSS should be limited to small fixes in `static/css/app.css`.
- JavaScript should be limited to Alpine snippets and tiny app behavior in `static/js/app.js`.

## Data Model

`accounts.User` extends `AbstractUser` and includes:

- `role`: `student` or `admin`.
- Optional student profile fields such as `student_id`, `department`, `avatar`, and `bio`.
- Timestamp fields through Django defaults where helpful.

`posts.Post` includes:

- `author`: foreign key to user.
- `title`, `description`, `category`, optional `image`.
- `status`: pending, approved, removed.
- Timestamps.
- Helper properties for like count, heart count, comment count, report count, and trending score.

`interactions.Comment` includes:

- `post`, `author`, optional `parent` for threaded comments.
- `body`, moderation status, timestamps.

`interactions.Reaction` includes:

- `post`, `user`, `kind` where kind is `like` or `heart`.
- A uniqueness constraint on `post`, `user`, and `kind`.

`interactions.Report` includes:

- Reporter, reason, details, status, timestamps.
- A target post and optional target comment.
- Admin review fields for resolution.

## User Flows

Student flow:

1. Student registers or logs in.
2. Student is redirected to the feed.
3. Student creates an idea or concern from a modal or dedicated form.
4. Feed updates show posts with category, status, image, counters, and comments.
5. Student reacts, comments, edits own posts, deletes own posts, reports content, and reviews their profile.

Admin flow:

1. Admin logs in.
2. Admin is redirected to the dashboard.
3. Admin reviews totals, active students, most reported content, and engagement metrics.
4. Admin approves/removes posts, moderates comments, and resolves reports.

## HTMX Behavior

HTMX endpoints return partial templates, not JSON, for user-facing interactions:

- Toggle like.
- Toggle heart.
- Add comment.
- Delete comment where permitted.
- Report post/comment.
- Delete post from feed where permitted.
- Load more feed items or switch sort mode.

Every HTMX endpoint must also work safely with normal Django permissions and CSRF protection. If a user is not authenticated, return `401` for HTMX requests or redirect to login for normal requests. If a user is authenticated but not authorized, return `403` with a compact error partial for HTMX requests or the standard Django forbidden response for normal requests.

## UI/UX Direction

Use the README color theme:

- Primary: Royal Blue `#2C3E94`.
- Accent: Sky Blue `#5DADE2`.
- Success: Mint Green `#A9DFBF`.
- Background: Soft White `#FDFEFE`.

The interface should feel like an operational campus dashboard, not a marketing landing page. The first screen after login should be the product experience: feed for students, dashboard for admins.

Required UI patterns:

- Collapsible mobile sidebar.
- Dense but readable dashboard cards.
- Feed cards with clear title, category, status, author, time, reaction counts, and comment count.
- Icon-forward reaction and action buttons.
- Modal create/edit post form using Alpine.js.
- Mobile-first layouts that do not rely on wide screens.

## Error Handling and Permissions

- Anonymous users can only access login/register pages.
- Students can edit/delete only their own posts and comments.
- Admins can moderate all posts, comments, and reports.
- Removed content should not appear in the normal student feed.
- Validation errors should render next to form fields.
- HTMX requests should return partials that preserve context after validation errors.
- Non-HTMX requests should fall back to full-page redirects or rendered forms.

## Testing Strategy

Phase 1 tests should cover:

- Custom user creation and role redirection.
- Post creation, ownership edits, ownership deletes, and status visibility.
- Reaction toggle behavior and uniqueness constraints.
- Comment creation and threaded parent behavior.
- Report creation and admin resolution.
- Dashboard metrics.
- HTMX endpoint responses and key partial rendering.
- Permission denials for anonymous users and unauthorized students.

Tests should use Django's built-in test runner unless the implementation plan chooses an already-installed pytest setup. The current repository does not show a pytest configuration, so Django tests are the conservative default.

## Phase Boundaries

Phase 1 is complete when a student and an admin can use the core system end-to-end in the browser with HTMX interactions.

Phase 2 is complete when the full README feature set is represented in working features or explicit ready hooks: trending, search/filter, richer analytics, tags, notification polling readiness, email verification readiness, and PostgreSQL-ready settings.

Phase 3 is complete when the application has polished mobile and desktop UI states across student and admin workflows, including empty states, loading states, validation states, and responsive sidebar behavior.

## Open Decisions Resolved

- Build order is Phase 1, then Phase 2, then Phase 3.
- Use modular apps instead of the existing empty `core` app.
- Keep Django Templates as the only frontend rendering system.
- Use Tailwind CDN, HTMX, and Alpine.js as specified.
- Treat the README as the product requirements source of truth.
