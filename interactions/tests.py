from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from posts.models import Post

from .models import Comment, Reaction, Report


class InteractionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
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

    def test_reaction_bar_renders_clean_like_icon(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("interactions:get_reaction_bar", args=[self.post.pk]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cv-like-icon")
        self.assertNotContains(response, "\u00f0\u0178")
        self.assertNotContains(response, "\u00e2\u009d")

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

    def test_add_comment(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("interactions:add_comment", args=[self.post.pk]),
            {"body": "I agree with this."},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)

    def test_report_post(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("interactions:report_post", args=[self.post.pk]),
            {"reason": Report.REASON_INAPPROPRIATE, "details": "Contains personal attacks."},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.count(), 1)
