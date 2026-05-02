# Comment Modal Design

## Goal

Make commenting feel like the supplied Facebook-style reference: clicking a post's Comment action opens a focused post modal, and comment owners can edit or delete their own comments from a three-dot menu.

## Approved Direction

Use the Modal Primary approach. Feed cards keep the main post summary and action row, while the full comment experience lives in a centered modal. This avoids crowding the feed and matches the reference image where the post, media, stats, reactions, and comment composer are all visible in one focused overlay.

## User Experience

Each feed post has a Like, Comment, and Share action row with consistent icon sizing and spacing. The Comment action opens a darkened overlay with a centered modal. The modal header reads "`<author name>`'s Post" and includes a close button. The modal body shows the post content/media, stats, the Like/Comment/Share action row, the "Most relevant" label, the comments list, and the comment composer at the bottom.

Top-level comments and replies render as compact rows with an avatar, rounded bubble, author name, body text, timestamp, Like, Reply, and reaction count. For a comment owned by the current user, a three-dot menu appears beside the bubble. That menu contains Edit and Delete. Campus admins keep moderation capability, but ordinary users only see owner actions for their own comments.

Editing a comment opens an inline edit composer in place, using the same mention-aware editor style as creating comments. Save updates the comment and refreshes the relevant comments area. Cancel restores the normal comment row without changing the comment. Delete removes the comment after submission and refreshes the comments area.

## Architecture

The Django views remain HTMX-first. Posts gain a modal partial endpoint that renders one post in a modal shell. The existing reaction, share, comment, and mention behavior is reused inside that partial so the modal stays in sync with existing server-side behavior.

Comment editing adds a focused pair of interaction views: one GET view to render the edit form partial, and one POST path to save changes through `CommentForm`. Permission checks live in the view and allow only the comment author or a campus admin to edit/delete. Comment list rendering should remain a reusable partial so feed refreshes and modal refreshes share the same markup.

## Components

- `posts.views`: add a post modal endpoint that loads the approved post with author, attachments, comments, replies, mentions, and reactions.
- `posts.urls`: add a route for the modal endpoint.
- `templates/posts/partials/post_modal.html`: create the overlay and modal layout.
- `templates/interactions/partials/reaction_bar.html`: adjust the Comment action to open the modal and keep Like/Share behavior.
- `templates/interactions/partials/comment_list.html`: render comment rows in the approved compact style with owner menu support.
- `templates/interactions/partials/comment_actions.html`: keep Like/Reply/reaction behavior, but move Edit/Delete into the owner menu area instead of exposing plain action links.
- `templates/interactions/partials/comment_edit_form.html`: create the inline edit form.
- `interactions.views`: add comment edit GET/POST handling and reuse existing comment-list refresh logic.
- `interactions.urls`: add routes for comment edit.
- `static/css/app.css`: add modal, comment menu, and compact comment styling only where Tailwind utility classes are not enough.
- `interactions.tests` and `posts.tests`: cover permission, edit behavior, modal rendering, and action-row/modal wiring.

## Data Flow

1. User clicks Comment on a feed post.
2. HTMX requests the post modal partial and swaps it into a page-level modal target.
3. User adds, edits, deletes, replies to, or reacts to comments.
4. The server validates permissions and form data.
5. HTMX refreshes the modal comments area, preserving the same post modal shell.

## Error Handling

Invalid comment bodies return the edit or create form with validation status `400`. Unauthorized edit/delete attempts raise `PermissionDenied`. Non-POST mutation requests return `400`, matching the existing interaction views.

## Testing

Tests must prove the modal renders the post and comment UI, the Comment action targets the modal endpoint, comment owners can access edit/delete controls, non-owners cannot edit/delete, valid edits update the comment body, and invalid edits return validation errors without changing the stored comment.
