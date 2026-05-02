# Ehance UI Design Spec

## Goal

Use the empty desktop space on the left and right of the feed to make CampusVoice feel more complete, useful, and balanced without crowding the central post experience.

## Current Problem

The current feed is centered in a `max-w-[680px]` wrapper in `templates/base.html`. On wide screens this leaves large blank areas on both sides, as seen in the screenshot. The feed itself is readable, but the page feels unfinished because the surrounding space does not support navigation, discovery, or context.

## Recommended Approach

Use a responsive three-column feed layout on desktop:

- Left rail: user identity, create-post shortcut, feed navigation, category shortcuts.
- Center rail: the existing feed, create-post card, filters, posts, comments, and reactions.
- Right rail: campus activity summary, trending posts, posting guidelines, and admin status legend.

This is better than simply widening the feed because wide post cards make text and images harder to scan. It is also better than decorative side backgrounds because the space should help students navigate and understand campus activity.

## Layout Behavior

Desktop at `lg` and above:

- Page content uses a centered shell around `1180px` to `1280px`.
- Left rail is about `260px`.
- Center feed remains about `620px` to `680px`.
- Right rail is about `280px`.
- Side rails use `position: sticky` below the fixed top nav.
- Cards use the existing `cv-card` style and 8px radius.

Tablet and mobile below `lg`:

- Side rails are hidden.
- The existing single-column feed remains the primary experience.
- Filters remain usable and wrap naturally.
- No content should overlap or require horizontal scrolling.

## Left Rail Content

The left rail should feel like useful navigation, not decoration:

- Compact signed-in user card with avatar, name, and department if available.
- Primary action button: create a post.
- Feed shortcuts:
  - Latest
  - Most Liked
  - Trending
- Category shortcuts:
  - Suggestion
  - Complaint
  - Improvement
  - Event Idea

The active sort and category should match the current query string state.

## Right Rail Content

The right rail should help users understand what is happening on campus:

- Campus activity card:
  - Approved post count.
  - Total visible comment count.
  - Total post reaction count.
- Trending now card:
  - Up to three approved posts ordered by reactions, comments, then creation time.
  - Each item shows title, category, and compact counts.
- Posting guide card:
  - Keep it specific.
  - Respect other students.
  - Add a photo only when it helps explain the issue.
- Admin status legend:
  - Under Review
  - Planned
  - In Progress
  - Completed

## Data Requirements

The feed view should provide a small `feed_sidebar` context object:

- `approved_post_count`
- `visible_comment_count`
- `post_reaction_count`
- `trending_posts`

`trending_posts` should be independent from the current feed filter so the right rail always stays useful.

## Accessibility

- Side rail links must use real anchors.
- Icon-only or compact actions need clear text or `aria-label`.
- Sticky sidebars must not trap focus.
- Mobile must not hide unique actions; create post remains available in the main feed and top nav.

## Styling Direction

Keep the current Facebook-inspired CampusVoice style:

- White cards on `#f0f2f5`.
- Blue primary accents.
- Green secondary accents only for create or positive action.
- Small, dense cards with clear headings.
- No oversized hero sections, marketing copy, or decorative empty cards.

## Acceptance Criteria

- Desktop no longer has empty left and right space around the feed.
- Center feed remains readable and does not become wider than the existing design intent.
- Left rail provides navigation and category shortcuts.
- Right rail provides activity, trending posts, posting guidance, and admin status context.
- Mobile layout remains single-column and clean.
- Existing feed sorting, category filtering, infinite scroll, reactions, comments, and reports continue working.
