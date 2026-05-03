from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Friendship
from notifications.models import Mention, Notification
from posts.models import Post

from .models import Comment, Reaction, Report


class InteractionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
        )
        self.friend = get_user_model().objects.create_user(
            username="lanz",
            email="lanz@example.com",
            password="StrongPass123",
        )
        Friendship.objects.create(
            requester=self.user,
            addressee=self.friend,
            status=Friendship.STATUS_ACCEPTED,
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Improve Wi-Fi",
            description="Coverage is weak near the lab.",
            category=Post.CATEGORY_COMPLAINT,
        )

    def test_toggle_like_creates_and_removes_reaction(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(reverse("interactions:toggle_reaction", args=[self.post.pk, "like"]), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reaction.objects.count(), 1)

        self.client.post(reverse("interactions:toggle_reaction", args=[self.post.pk, "like"]), HTTP_HX_REQUEST="true")
        self.assertEqual(Reaction.objects.count(), 0)

    def test_switching_post_reaction_replaces_previous_choice(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        self.client.post(reverse("interactions:toggle_reaction", args=[self.post.pk, "like"]), HTTP_HX_REQUEST="true")
        response = self.client.post(reverse("interactions:toggle_reaction", args=[self.post.pk, "love"]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reaction.objects.count(), 1)
        self.assertEqual(Reaction.objects.get().kind, "love")
        self.assertContains(response, 'data-current-reaction="love"')
        self.assertContains(response, 'aria-pressed="true"')

    def test_modal_post_reaction_updates_modal_targets(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            f"{reverse('interactions:toggle_reaction', args=[self.post.pk, 'like'])}?modal=1",
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'id="modal-post-stats-{self.post.pk}"')
        self.assertContains(response, 'hx-swap-oob="outerHTML"')
        self.assertContains(response, 'aria-label="1 reaction')
        self.assertContains(response, f'id="post-stats-{self.post.pk}"')

    def test_reaction_bar_renders_clean_like_icon(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("interactions:get_reaction_bar", args=[self.post.pk]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cv-like-icon")
        self.assertNotContains(response, "\u00f0\u0178")
        self.assertNotContains(response, "\u00e2\u009d")

    def test_reaction_main_button_quick_click_defaults_to_like(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("interactions:get_reaction_bar", args=[self.post.pk]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-default-reaction-kind="like"')
        self.assertContains(response, "pulseDefaultReaction($el)")
        self.assertNotContains(response, "!showPicker")
        self.assertContains(response, "data-quick-reaction-url")

    def test_reaction_picker_uses_facebook_style_layout(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("interactions:get_reaction_bar", args=[self.post.pk]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cv-fb-reaction-picker")
        self.assertContains(response, "cv-fb-reaction-option")
        self.assertContains(response, "cv-fb-reaction-like")
        self.assertContains(response, "cv-fb-reaction-love")
        self.assertContains(response, "cv-fb-reaction-care")

    def test_post_stats_uses_compact_facebook_style_counts(self):
        self.client.login(email="student@example.com", password="StrongPass123")
        Reaction.objects.create(post=self.post, user=self.friend, kind=Reaction.KIND_LOVE)
        Comment.objects.create(post=self.post, author=self.friend, body="This matters.")

        response = self.client.get(reverse("posts:feed"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cv-fb-engagement-strip")
        self.assertContains(response, "cv-fb-count-item")
        self.assertContains(response, "cv-fb-reaction-stack")
        self.assertContains(response, "1")

    def test_comment_reactions_can_switch_without_affecting_post_reactions(self):
        self.client.login(email="student@example.com", password="StrongPass123")
        comment = Comment.objects.create(post=self.post, author=self.user, body="I agree.")

        self.client.post(reverse("interactions:toggle_reaction", args=[self.post.pk, "like"]), HTTP_HX_REQUEST="true")
        self.client.post(reverse("interactions:toggle_comment_reaction", args=[comment.pk, "like"]), HTTP_HX_REQUEST="true")
        response = self.client.post(reverse("interactions:toggle_comment_reaction", args=[comment.pk, "haha"]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reaction.objects.filter(post=self.post, comment__isnull=True).get().kind, "like")
        self.assertEqual(Reaction.objects.filter(comment=comment).count(), 1)
        self.assertEqual(Reaction.objects.get(comment=comment).kind, "haha")

    def test_comment_owner_sees_edit_delete_menu(self):
        comment = Comment.objects.create(post=self.post, author=self.user, body="Owner comment")
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("posts:modal", args=[self.post.pk]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aria-label="Comment options"')
        self.assertContains(response, f'hx-get="{reverse("interactions:edit_comment", args=[comment.pk])}?modal=1"')
        self.assertContains(response, f'hx-post="{reverse("interactions:delete_comment", args=[comment.pk])}?modal=1"')
        self.assertContains(response, "Edit")
        self.assertContains(response, "Delete")

    def test_non_owner_does_not_see_comment_owner_menu(self):
        owner = get_user_model().objects.create_user(username="owner", email="owner@example.com", password="StrongPass123")
        Comment.objects.create(post=self.post, author=owner, body="Someone else's comment")
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("posts:modal", args=[self.post.pk]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'aria-label="Comment options"')
        self.assertNotContains(response, "Edit")
        self.assertNotContains(response, "Delete")

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
        self.assertContains(response, 'hx-target="#post-modal-root"')
        self.assertContains(response, 'hx-swap="innerHTML"')

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

    def test_invalid_comment_edit_returns_errors_without_changing_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.user, body="Original comment")
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("interactions:edit_comment", args=[comment.pk]),
            {"body": ""},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 400)
        comment.refresh_from_db()
        self.assertEqual(comment.body, "Original comment")
        self.assertContains(response, "Edit comment", status_code=400)

    def test_add_comment(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("interactions:add_comment", args=[self.post.pk]),
            {"body": "I agree with this."},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)

    def test_modal_add_comment_updates_modal_comments_and_count(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            f"{reverse('interactions:add_comment', args=[self.post.pk])}?modal=1",
            {"body": "Modal comment"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertContains(response, f'id="modal-comments-{self.post.pk}"')
        self.assertContains(response, "Modal comment")
        self.assertContains(response, f'id="modal-post-stats-{self.post.pk}"')
        self.assertContains(response, f'id="post-stats-{self.post.pk}"')
        self.assertContains(response, "1 comment")
        self.assertContains(response, 'hx-swap-oob="outerHTML"')

    def test_comment_form_uses_highlightable_mention_editor(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("interactions:add_comment", args=[self.post.pk]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'type="hidden" name="body"')
        self.assertContains(response, "data-mention-editor")
        self.assertContains(response, "contenteditable")
        self.assertContains(response, "mentionComposer")

    def test_reply_form_supports_friend_mentions(self):
        comment = Comment.objects.create(post=self.post, author=self.user, body="Initial thought")
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("interactions:add_reply", args=[comment.pk]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'type="hidden" name="body"')
        self.assertContains(response, "data-mention-editor")
        self.assertContains(response, "contenteditable")
        self.assertContains(response, "mentionComposer")

    def test_reply_mentions_notify_accepted_friends(self):
        comment = Comment.objects.create(post=self.post, author=self.user, body="Initial thought")
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("interactions:add_reply", args=[comment.pk]),
            {"body": "Looping in @lanz"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        reply = Comment.objects.get(parent=comment)
        self.assertEqual(Mention.objects.filter(comment=reply, recipient=self.friend).count(), 1)
        self.assertEqual(Notification.objects.filter(recipient=self.friend, kind=Notification.KIND_MENTION_COMMENT).count(), 1)

    def test_report_post(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("interactions:report_post", args=[self.post.pk]),
            {"reason": Report.REASON_INAPPROPRIATE, "details": "Contains personal attacks."},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.count(), 1)
