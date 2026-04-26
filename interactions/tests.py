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