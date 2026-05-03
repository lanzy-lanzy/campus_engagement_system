# Comment Modal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Facebook-style post comment modal where clicking Comment opens the focused comment experience and comment owners can edit/delete through a three-dot menu.

**Architecture:** Keep the feature HTMX-first. Add a post modal endpoint in `posts`, reuse the existing post/comment/reaction partials where possible, and add a small comment edit endpoint in `interactions`. The feed should render a modal target and use the action row to open modal content without navigating away.

**Tech Stack:** Django views/templates/tests, HTMX, Alpine.js, Tailwind utility classes, existing `mentionComposer` JavaScript, `python manage.py test`.

---

## File Structure

- Modify `posts/tests.py`: add tests for modal rendering and feed action wiring.
- Modify `posts/views.py`: add a `post_modal` view and a helper/query pattern for loading post modal data.
- Modify `posts/urls.py`: add the modal route.
- Modify `templates/posts/feed.html`: add one page-level modal root.
- Modify `templates/posts/partials/post_card.html`: remove the inline comments block from the feed card.
- Create `templates/posts/partials/post_modal.html`: centered overlay with post content, stats, action row, comments, composer, and close button.
- Modify `templates/interactions/partials/reaction_bar.html`: change primary actions to Like, Comment, Share and wire Comment to the post modal.
- Modify `interactions/tests.py`: add comment edit and owner menu permission tests.
- Modify `interactions/views.py`: add `edit_comment` and a helper for rendering refreshed comment lists.
- Modify `interactions/urls.py`: add comment edit route.
- Create `templates/interactions/partials/comment_edit_form.html`: inline edit form using the mention editor.
- Modify `templates/interactions/partials/comment_list.html`: render compact comment rows and owner menu targets.
- Modify `templates/interactions/partials/comment_actions.html`: keep Like/Reply/reaction behavior and remove plain Delete/Hide owner links from the normal action line.
- Modify `static/css/app.css`: add modal and compact comment polish where utility classes are too noisy.

---

### Task 1: Post Modal Endpoint

**Files:**
- Modify: `posts/tests.py`
- Modify: `posts/views.py`
- Modify: `posts/urls.py`
- Create: `templates/posts/partials/post_modal.html`

- [ ] **Step 1: Write the failing modal rendering test**

Add this test to `PostViewTests` in `posts/tests.py`:

```python
def test_post_modal_renders_post_actions_and_comments(self):
    post = Post.objects.create(
        author=self.user,
        title="Next.js Folder Structure",
        description="Understand project architecture at a glance.",
        category=Post.CATEGORY_SUGGESTION,
        status=Post.STATUS_APPROVED,
    )
    Comment.objects.create(post=post, author=self.user, body="gg")
    self.client.login(email="student@example.com", password="StrongPass123")

    response = self.client.get(reverse("posts:modal", args=[post.pk]), HTTP_HX_REQUEST="true")

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "student's Post")
    self.assertContains(response, "Next.js Folder Structure")
    self.assertContains(response, "Most relevant")
    self.assertContains(response, "gg")
    self.assertContains(response, 'id="post-modal"')
    self.assertContains(response, "Like")
    self.assertContains(response, "Comment")
    self.assertContains(response, "Share")
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
python manage.py test posts.tests.PostViewTests.test_post_modal_renders_post_actions_and_comments
```

Expected: FAIL with `Reverse for 'modal' not found` or a 404 because the modal route does not exist yet.

- [ ] **Step 3: Add the modal route**

In `posts/urls.py`, add this route before edit/delete routes:

```python
path("posts/<int:pk>/modal/", views.post_modal, name="modal"),
```

- [ ] **Step 4: Add the modal view**

In `posts/views.py`, add this view after `share_post`:

```python
@login_required
def post_modal(request, pk):
    post = get_object_or_404(
        Post.objects.filter(status=Post.STATUS_APPROVED)
        .select_related("author", "shared_from__author")
        .prefetch_related(
            "attachments",
            "shared_from__attachments",
            "mentions__recipient",
            "comments__author",
            "comments__mentions__recipient",
            "comments__replies__author",
            "comments__replies__mentions__recipient",
            "tags",
        ),
        pk=pk,
    )
    comments = post.comments.filter(parent__isnull=True, status=Comment.STATUS_VISIBLE).select_related("author").prefetch_related(
        "mentions__recipient",
        "replies__author",
        "replies__mentions__recipient",
        "replies__reactions",
        "reactions",
    )
    return render(request, "posts/partials/post_modal.html", {"post": post, "comments": comments})
```

- [ ] **Step 5: Create the modal partial**

Create `templates/posts/partials/post_modal.html` with:

```django
{% load interaction_tags notification_tags %}
<div id="post-modal-root" class="cv-modal-backdrop" x-data="{ open: true }" x-show="open" x-cloak>
  <div class="cv-post-modal" id="post-modal" role="dialog" aria-modal="true" aria-labelledby="post-modal-title">
    <header class="cv-post-modal-header">
      <h2 id="post-modal-title">{{ post.author.get_full_name|default:post.author.username }}'s Post</h2>
      <button type="button" class="cv-modal-close" aria-label="Close" @click="open = false; setTimeout(() => $root.remove(), 150)">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
    </header>
    <div class="cv-post-modal-body">
      <div class="px-4 pt-3 pb-2">
        {% if post.is_shared_post %}
          {% if post.description %}
            <p class="whitespace-pre-line text-[15px] leading-relaxed text-[#1c1e21] mb-3">{{ post.description|mentionize:post }}</p>
          {% endif %}
          {% include "posts/partials/shared_post_preview.html" %}
        {% else %}
          <h3 class="text-[17px] font-semibold text-[#050505] mb-1">{{ post.title|mentionize:post }}</h3>
          <p class="whitespace-pre-line text-[15px] leading-relaxed text-[#1c1e21]">{{ post.description|mentionize:post }}</p>
        {% endif %}
      </div>
      {% if not post.is_shared_post %}
        {% include "posts/partials/post_media_grid.html" with post=post %}
      {% endif %}
      {% include "interactions/partials/post_stats.html" with post=post %}
      <hr class="cv-divider mx-4">
      <div class="px-2 py-1">
        {% include "interactions/partials/reaction_bar.html" with in_modal=True %}
      </div>
      {% include "posts/partials/share_slot.html" with post=post %}
      <hr class="cv-divider mx-4">
      <section class="px-4 py-3">
        {% include "interactions/partials/comment_list.html" with post=post comments=comments form=None %}
      </section>
    </div>
  </div>
</div>
```

- [ ] **Step 6: Run the test to verify it passes**

Run:

```powershell
python manage.py test posts.tests.PostViewTests.test_post_modal_renders_post_actions_and_comments
```

Expected: PASS.

---

### Task 2: Feed Action Row Opens Modal

**Files:**
- Modify: `posts/tests.py`
- Modify: `templates/posts/feed.html`
- Modify: `templates/posts/partials/post_card.html`
- Modify: `templates/interactions/partials/reaction_bar.html`

- [ ] **Step 1: Write the failing feed wiring test**

Add this test to `PostViewTests`:

```python
def test_feed_comment_action_targets_post_modal(self):
    post = Post.objects.create(
        author=self.user,
        title="Open comments in modal",
        description="The feed should stay clean.",
        category=Post.CATEGORY_SUGGESTION,
        status=Post.STATUS_APPROVED,
    )
    self.client.login(email="student@example.com", password="StrongPass123")

    response = self.client.get(reverse("posts:feed"))

    self.assertContains(response, 'id="post-modal-root"')
    self.assertContains(response, f'hx-get="{reverse("posts:modal", args=[post.pk])}"')
    self.assertContains(response, 'hx-target="#post-modal-root"')
    self.assertContains(response, "Comment")
    self.assertContains(response, "Share")
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
python manage.py test posts.tests.PostViewTests.test_feed_comment_action_targets_post_modal
```

Expected: FAIL because the feed does not expose a modal root or a Comment action yet.

- [ ] **Step 3: Add the page-level modal root**

In `templates/posts/feed.html`, add this after the feed shell closing `</div>` and before `{% endblock %}`:

```django
<div id="post-modal-root"></div>
```

- [ ] **Step 4: Remove inline comments from feed cards**

In `templates/posts/partials/post_card.html`, remove this block from the bottom of the card:

```django
<hr class="cv-divider mx-4">
<div class="px-4 py-3">
  {% include "interactions/partials/comment_list.html" with post=post comments=post.comments.all form=None %}
</div>
```

- [ ] **Step 5: Change the action row to Like, Comment, Share**

In `templates/interactions/partials/reaction_bar.html`, replace the second and third action blocks after the Like block with:

```django
<div class="flex-1">
  <button type="button" class="cv-react-btn w-full" hx-get="{% url 'posts:modal' post.pk %}" hx-target="#post-modal-root" hx-swap="outerHTML">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h8m-8 4h5m8-4c0 4.418-4.03 8-9 8a9.86 9.86 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
    <span>Comment</span>
  </button>
</div>
<div class="flex-1">
  <button type="button" class="cv-react-btn w-full" hx-get="{% url 'posts:share' post.pk %}" hx-target="#share-{{ post.pk }}" hx-swap="outerHTML">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12s-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-9.316l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 12.632a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"></path></svg>
    <span>Share</span>
  </button>
</div>
```

Keep the existing `<div id="report-{{ post.pk }}"></div>` only if another UI still triggers it; otherwise remove it from this primary action row.

- [ ] **Step 6: Run the feed wiring test**

Run:

```powershell
python manage.py test posts.tests.PostViewTests.test_feed_comment_action_targets_post_modal
```

Expected: PASS.

---

### Task 3: Comment Owner Menu Markup

**Files:**
- Modify: `interactions/tests.py`
- Modify: `templates/interactions/partials/comment_list.html`
- Modify: `templates/interactions/partials/comment_actions.html`

- [ ] **Step 1: Write the failing owner menu test**

Add this test to `InteractionTests`:

```python
def test_comment_owner_sees_edit_delete_menu(self):
    comment = Comment.objects.create(post=self.post, author=self.user, body="Owner comment")
    self.client.login(email="student@example.com", password="StrongPass123")

    response = self.client.get(reverse("posts:modal", args=[self.post.pk]), HTTP_HX_REQUEST="true")

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'aria-label="Comment options"')
    self.assertContains(response, f'hx-get="{reverse("interactions:edit_comment", args=[comment.pk])}"')
    self.assertContains(response, f'hx-post="{reverse("interactions:delete_comment", args=[comment.pk])}"')
    self.assertContains(response, "Edit")
    self.assertContains(response, "Delete")
```

- [ ] **Step 2: Write the failing non-owner menu test**

Add this test to `InteractionTests`:

```python
def test_non_owner_does_not_see_comment_owner_menu(self):
    owner = get_user_model().objects.create_user(username="owner", email="owner@example.com", password="StrongPass123")
    Comment.objects.create(post=self.post, author=owner, body="Someone else's comment")
    self.client.login(email="student@example.com", password="StrongPass123")

    response = self.client.get(reverse("posts:modal", args=[self.post.pk]), HTTP_HX_REQUEST="true")

    self.assertEqual(response.status_code, 200)
    self.assertNotContains(response, 'aria-label="Comment options"')
    self.assertNotContains(response, "Edit")
    self.assertNotContains(response, "Delete")
```

- [ ] **Step 3: Run the tests to verify they fail**

Run:

```powershell
python manage.py test interactions.tests.InteractionTests.test_comment_owner_sees_edit_delete_menu interactions.tests.InteractionTests.test_non_owner_does_not_see_comment_owner_menu
```

Expected: first test FAILS because edit route/menu do not exist; second may fail if plain Delete is still shown.

- [ ] **Step 4: Add owner menu markup in comment list**

In `templates/interactions/partials/comment_list.html`, structure each top-level comment row like this:

```django
<div class="flex items-start gap-2 group" id="comment-{{ comment.pk }}">
  <div class="cv-avatar-placeholder w-8 h-8 text-xs bg-gradient-to-br from-[#65676b] to-[#8a8d91]">{{ comment.author.username|first|upper }}</div>
  <div class="flex-1 min-w-0">
    <div class="flex items-center gap-1">
      <div class="inline-block bg-[#f0f2f5] rounded-2xl px-3 py-2 max-w-full">
        <span class="font-semibold text-[13px] text-[#050505]">{{ comment.author.get_full_name|default:comment.author.username }}</span>
        <p class="text-[15px] text-[#1c1e21] leading-snug">{{ comment.body|mentionize:comment }}</p>
      </div>
      {% if comment.author == user or user.is_campus_admin %}
        <div class="relative" x-data="{ open: false }" @click.outside="open = false">
          <button type="button" class="cv-comment-menu-button" aria-label="Comment options" @click="open = !open">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true"><circle cx="4" cy="10" r="1.5"/><circle cx="10" cy="10" r="1.5"/><circle cx="16" cy="10" r="1.5"/></svg>
          </button>
          <div x-show="open" x-transition class="cv-dropdown cv-comment-dropdown left-0 right-auto min-w-[180px]" x-cloak>
            <button type="button" hx-get="{% url 'interactions:edit_comment' comment.pk %}" hx-target="#comment-{{ comment.pk }}" hx-swap="outerHTML">Edit</button>
            <form method="post" action="{% url 'interactions:delete_comment' comment.pk %}" hx-post="{% url 'interactions:delete_comment' comment.pk %}" hx-target="#comments-{{ post.pk }}" hx-swap="outerHTML">
              {% csrf_token %}
              <button type="submit" class="text-red-600">Delete</button>
            </form>
          </div>
        </div>
      {% endif %}
    </div>
    {% include "interactions/partials/comment_actions.html" with comment=comment post=post %}
    <div id="reply-form-{{ comment.pk }}"></div>
  </div>
</div>
```

Apply the same compact pattern to replies, using `id="comment-{{ reply.pk }}"` and a smaller avatar.

- [ ] **Step 5: Remove plain Delete/Hide from normal action line**

In `templates/interactions/partials/comment_actions.html`, remove the trailing Hide and Delete forms from the standard action row. Keep timestamp, Reply, comment reaction button, reaction picker, and reaction counts.

- [ ] **Step 6: Add the edit URL temporarily or continue to Task 4 before re-running**

Because this task references `interactions:edit_comment`, either add the URL shell from Task 4 first or expect `NoReverseMatch`. The owner-menu tests should pass after Task 4 adds the route and view.

---

### Task 4: Comment Edit Endpoint and Form

**Files:**
- Modify: `interactions/tests.py`
- Modify: `interactions/views.py`
- Modify: `interactions/urls.py`
- Create: `templates/interactions/partials/comment_edit_form.html`

- [ ] **Step 1: Write the failing GET edit form test**

Add this test to `InteractionTests`:

```python
def test_comment_owner_can_open_edit_form(self):
    comment = Comment.objects.create(post=self.post, author=self.user, body="Original comment")
    self.client.login(email="student@example.com", password="StrongPass123")

    response = self.client.get(reverse("interactions:edit_comment", args=[comment.pk]), HTTP_HX_REQUEST="true")

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "Original comment")
    self.assertContains(response, 'type="hidden" name="body"')
    self.assertContains(response, "data-mention-editor")
    self.assertContains(response, "Save")
    self.assertContains(response, "Cancel")
```

- [ ] **Step 2: Write the failing POST edit test**

Add this test to `InteractionTests`:

```python
def test_comment_owner_can_update_comment(self):
    comment = Comment.objects.create(post=self.post, author=self.user, body="Original comment")
    self.client.login(email="student@example.com", password="StrongPass123")

    response = self.client.post(
        reverse("interactions:edit_comment", args=[comment.pk]),
        {"body": "Updated comment"},
        HTTP_HX_REQUEST="true",
    )

    self.assertEqual(response.status_code, 200)
    comment.refresh_from_db()
    self.assertEqual(comment.body, "Updated comment")
    self.assertContains(response, "Updated comment")
    self.assertContains(response, f'id="comments-{self.post.pk}"')
```

- [ ] **Step 3: Write the failing permission test**

Add this test to `InteractionTests`:

```python
def test_non_owner_cannot_update_comment(self):
    owner = get_user_model().objects.create_user(username="owner", email="owner@example.com", password="StrongPass123")
    comment = Comment.objects.create(post=self.post, author=owner, body="Private edit")
    self.client.login(email="student@example.com", password="StrongPass123")

    response = self.client.post(
        reverse("interactions:edit_comment", args=[comment.pk]),
        {"body": "Hijacked"},
        HTTP_HX_REQUEST="true",
    )

    self.assertEqual(response.status_code, 403)
    comment.refresh_from_db()
    self.assertEqual(comment.body, "Private edit")
```

- [ ] **Step 4: Run the tests to verify they fail**

Run:

```powershell
python manage.py test interactions.tests.InteractionTests.test_comment_owner_can_open_edit_form interactions.tests.InteractionTests.test_comment_owner_can_update_comment interactions.tests.InteractionTests.test_non_owner_cannot_update_comment
```

Expected: FAIL with missing `edit_comment` route.

- [ ] **Step 5: Add the edit route**

In `interactions/urls.py`, add:

```python
path("comments/<int:comment_id>/edit/", views.edit_comment, name="edit_comment"),
```

- [ ] **Step 6: Add a comment-list helper and edit view**

In `interactions/views.py`, add this helper near `_htmx_error`:

```python
def _render_comment_list(request, post, status=200):
    comments = post.comments.filter(parent__isnull=True, status=Comment.STATUS_VISIBLE).select_related("author").prefetch_related(
        "mentions__recipient",
        "replies__author",
        "replies__mentions__recipient",
        "replies__reactions",
        "reactions",
    )
    return render(request, "interactions/partials/comment_list.html", {"post": post, "comments": comments, "form": CommentForm()}, status=status)
```

Then add:

```python
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment.objects.select_related("post", "author"), pk=comment_id)
    if comment.author != request.user and not request.user.is_campus_admin:
        raise PermissionDenied

    if request.method != "POST":
        form = CommentForm(instance=comment)
        return render(request, "interactions/partials/comment_edit_form.html", {"comment": comment, "post": comment.post, "form": form})

    form = CommentForm(request.POST, instance=comment)
    if form.is_valid():
        comment = form.save()
        process_mentions(request.user, comment.body, comment=comment)
        return _render_comment_list(request, comment.post)

    return render(
        request,
        "interactions/partials/comment_edit_form.html",
        {"comment": comment, "post": comment.post, "form": form},
        status=400,
    )
```

- [ ] **Step 7: Reuse the helper in existing comment mutations**

In `add_comment`, `add_reply`, `delete_comment`, and `hide_comment`, replace repeated comment-query render blocks with `_render_comment_list(request, post)` after successful mutations. Preserve the existing invalid form behavior for add/create paths.

- [ ] **Step 8: Create the edit form partial**

Create `templates/interactions/partials/comment_edit_form.html`:

```django
<div id="comment-{{ comment.pk }}" class="flex items-start gap-2">
  <div class="cv-avatar-placeholder w-8 h-8 text-xs bg-gradient-to-br from-[#65676b] to-[#8a8d91]">{{ comment.author.username|first|upper }}</div>
  <form method="post" action="{% url 'interactions:edit_comment' comment.pk %}" hx-post="{% url 'interactions:edit_comment' comment.pk %}" hx-target="#comments-{{ post.pk }}" hx-swap="outerHTML" class="flex-1 min-w-0">
    {% csrf_token %}
    <div class="relative" x-data="mentionComposer('{{ comment.body|escapejs }}')" x-init="init($refs.editor, $refs.body)">
      <input type="hidden" name="body" x-ref="body" value="{{ comment.body }}">
      <div
        x-ref="editor"
        data-mention-editor
        contenteditable="true"
        role="textbox"
        aria-label="Edit comment"
        data-placeholder="Edit comment"
        class="cv-mention-editor cv-comment-mention-editor"
        @input="onInput"
        @keydown="onKeydown"
        @blur="onBlur"></div>
      <div x-show="open" x-cloak class="mention-dropdown mention-dropdown-up">
        <template x-for="(friend, index) in friends" :key="friend.id">
          <button type="button" class="mention-item w-full text-left" :class="{ 'is-active': index === activeIndex }" @mousedown.prevent="selectFriend(index)">
            <span class="mention-item-avatar">
              <template x-if="friend.avatar_url"><img :src="friend.avatar_url" alt=""></template>
              <template x-if="!friend.avatar_url"><span x-text="initialFor(friend)"></span></template>
            </span>
            <span class="min-w-0">
              <span class="mention-item-name" x-text="friend.display_name || friend.username"></span>
              <span class="mention-item-meta" x-text="friend.department || ('@' + friend.username)"></span>
            </span>
          </button>
        </template>
      </div>
    </div>
    <div class="mt-1 ml-2 flex items-center gap-2">
      <button type="submit" class="text-[12px] font-semibold text-[#1877f2] hover:underline">Save</button>
      <button type="button" class="text-[12px] font-semibold text-[#65676b] hover:underline" hx-get="{% url 'posts:modal' post.pk %}" hx-target="#post-modal-root" hx-swap="outerHTML">Cancel</button>
    </div>
  </form>
</div>
```

- [ ] **Step 9: Run edit and owner menu tests**

Run:

```powershell
python manage.py test interactions.tests.InteractionTests.test_comment_owner_sees_edit_delete_menu interactions.tests.InteractionTests.test_non_owner_does_not_see_comment_owner_menu interactions.tests.InteractionTests.test_comment_owner_can_open_edit_form interactions.tests.InteractionTests.test_comment_owner_can_update_comment interactions.tests.InteractionTests.test_non_owner_cannot_update_comment
```

Expected: PASS.

---

### Task 5: Modal and Comment Visual Polish

**Files:**
- Modify: `static/css/app.css`
- Modify: `templates/interactions/partials/comment_list.html`

- [ ] **Step 1: Add a focused CSS smoke test**

Add this assertion to `test_post_modal_renders_post_actions_and_comments` in `posts/tests.py`:

```python
self.assertContains(response, "cv-modal-backdrop")
self.assertContains(response, "cv-post-modal")
self.assertContains(response, "cv-comment-menu-button")
```

- [ ] **Step 2: Run the test**

Run:

```powershell
python manage.py test posts.tests.PostViewTests.test_post_modal_renders_post_actions_and_comments
```

Expected: PASS if classes already exist in templates; FAIL if markup still needs class names.

- [ ] **Step 3: Add modal and menu CSS**

Append this focused CSS to `static/css/app.css` near the dropdown/comment styles:

```css
.cv-modal-backdrop {
  align-items: flex-start;
  background: rgba(0, 0, 0, .72);
  display: flex;
  inset: 0;
  justify-content: center;
  overflow-y: auto;
  padding: 28px 12px;
  position: fixed;
  z-index: 200;
}
.cv-post-modal {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, .35);
  max-width: 630px;
  overflow: hidden;
  width: min(100%, 630px);
}
.cv-post-modal-header {
  align-items: center;
  background: #242526;
  border-bottom: 1px solid #3a3b3c;
  color: #e4e6eb;
  display: flex;
  min-height: 56px;
  justify-content: center;
  padding: 0 56px;
  position: sticky;
  top: 0;
  z-index: 2;
}
.cv-post-modal-header h2 {
  font-size: 18px;
  font-weight: 800;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.cv-modal-close {
  align-items: center;
  background: #3a3b3c;
  border: 0;
  border-radius: 999px;
  color: #e4e6eb;
  cursor: pointer;
  display: inline-flex;
  height: 36px;
  justify-content: center;
  position: absolute;
  right: 12px;
  width: 36px;
}
.cv-modal-close:hover {
  background: #4e4f50;
}
.cv-post-modal-body {
  max-height: calc(100vh - 84px);
  overflow-y: auto;
}
.cv-comment-menu-button {
  align-items: center;
  background: #e4e6eb;
  border: 0;
  border-radius: 999px;
  color: #65676b;
  cursor: pointer;
  display: inline-flex;
  height: 30px;
  justify-content: center;
  width: 30px;
}
.cv-comment-menu-button:hover {
  background: #d8dadf;
  color: #050505;
}
.cv-comment-dropdown {
  top: calc(100% + 4px);
}
@media (max-width: 640px) {
  .cv-modal-backdrop {
    padding: 0;
  }
  .cv-post-modal {
    border-radius: 0;
    min-height: 100vh;
  }
  .cv-post-modal-body {
    max-height: calc(100vh - 56px);
  }
}
```

- [ ] **Step 4: Run the CSS smoke test**

Run:

```powershell
python manage.py test posts.tests.PostViewTests.test_post_modal_renders_post_actions_and_comments
```

Expected: PASS.

---

### Task 6: Regression and Manual Verification

**Files:**
- No new files.
- Verify changes across tests and browser.

- [ ] **Step 1: Run focused post and interaction tests**

Run:

```powershell
python manage.py test posts.tests.PostViewTests interactions.tests.InteractionTests
```

Expected: PASS.

- [ ] **Step 2: Run the full test suite**

Run:

```powershell
python manage.py test
```

Expected: PASS.

- [ ] **Step 3: Start the dev server**

Run:

```powershell
python manage.py runserver 127.0.0.1:8000
```

Expected: server starts without errors.

- [ ] **Step 4: Browser-check the UI**

Open `http://127.0.0.1:8000/` in the in-app browser. Log in with an existing local test account or create one through the app. Verify:

- Feed action row reads Like, Comment, Share.
- Comment opens a centered modal.
- Modal closes from the close button.
- Comment owner sees the three-dot menu.
- Edit opens the inline editor, Save updates the text, Cancel closes the editor without saving.
- Delete removes the comment.
- A non-owner does not see Edit/Delete on another user's comment.

- [ ] **Step 5: Check the working tree**

Run:

```powershell
git status --short
```

Expected: only intended files from this plan are changed, alongside any pre-existing user-owned changes that were already present before implementation.

---

## Self-Review

- Spec coverage: modal endpoint, Comment action, Like/Comment/Share row, comment owner Edit/Delete menu, inline edit, delete refresh, permission checks, and visual modal styling are covered by Tasks 1 through 6.
- Placeholder scan: the plan contains no TBD/TODO placeholders.
- Type consistency: route names are `posts:modal` and `interactions:edit_comment`; template IDs are `post-modal-root`, `post-modal`, `comments-{{ post.pk }}`, and `comment-{{ comment.pk }}` throughout.
