from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Post


class PostModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
        )

    def test_trending_score_counts_reactions_and_comments(self):
        post = Post.objects.create(
            author=self.user,
            title="Add study pods",
            description="Quiet spaces would help.",
            category=Post.CATEGORY_IMPROVEMENT,
        )

        self.assertEqual(post.trending_score, 0)


class PostViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
        )

    def test_student_can_create_post(self):
        self.client.login(email="student@example.com", password="StrongPass123")
        response = self.client.post(
            reverse("posts:create"),
            {
                "title": "More shaded benches",
                "description": "The courtyard needs shade.",
                "category": Post.CATEGORY_SUGGESTION,
            },
        )

        self.assertRedirects(response, reverse("posts:feed"))
        self.assertEqual(Post.objects.count(), 1)

    def test_student_cannot_edit_other_student_post(self):
        other = get_user_model().objects.create_user(username="other", email="other@example.com", password="StrongPass123")
        post = Post.objects.create(
            author=other,
            title="Library hours",
            description="Open earlier.",
            category=Post.CATEGORY_SUGGESTION,
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("posts:edit", args=[post.pk]))

        self.assertEqual(response.status_code, 403)

    def test_feed_renders_successfully(self):
        Post.objects.create(
            author=self.user,
            title="Test Post",
            description="Test Description",
            category=Post.CATEGORY_SUGGESTION,
            status=Post.STATUS_APPROVED,
        )
        self.client.login(email="student@example.com", password="StrongPass123")
        response = self.client.get(reverse("posts:feed"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Post")