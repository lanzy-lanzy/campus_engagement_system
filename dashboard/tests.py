from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from posts.models import Post


class DashboardTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
        )

    def test_admin_can_access_dashboard(self):
        self.client.login(email="admin@example.com", password="StrongPass123")
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 200)

    def test_non_admin_cannot_access_dashboard(self):
        user = get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
        )
        self.client.login(email="student@example.com", password="StrongPass123")
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_view_user_list(self):
        self.client.login(email="admin@example.com", password="StrongPass123")
        get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
        )

        response = self.client.get(reverse("dashboard:users"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "admin")
        self.assertContains(response, "student")
        self.assertContains(response, "Search")

    def test_admin_can_create_user(self):
        self.client.login(email="admin@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("dashboard:user_create"),
            {
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "StrongPass123",
                "first_name": "New",
                "last_name": "User",
                "role": "student",
                "department": "CS",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(email="newuser@example.com").exists())

    def test_admin_can_edit_user(self):
        target = get_user_model().objects.create_user(
            username="target",
            email="target@example.com",
            password="StrongPass123",
        )
        self.client.login(email="admin@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("dashboard:user_edit", args=[target.pk]),
            {
                "first_name": "Updated",
                "last_name": "Name",
                "role": "student",
                "department": "CS",
            },
        )

        self.assertEqual(response.status_code, 302)
        target.refresh_from_db()
        self.assertEqual(target.first_name, "Updated")

    def test_admin_can_toggle_user(self):
        target = get_user_model().objects.create_user(
            username="target",
            email="target@example.com",
            password="StrongPass123",
        )
        self.client.login(email="admin@example.com", password="StrongPass123")

        response = self.client.post(reverse("dashboard:user_toggle", args=[target.pk]))

        self.assertEqual(response.status_code, 302)
        target.refresh_from_db()
        self.assertFalse(target.is_active)

    def test_non_admin_cannot_access_users(self):
        user = get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("dashboard:users"))

        self.assertEqual(response.status_code, 403)

    def test_admin_can_view_post_list(self):
        Post.objects.create(
            author=self.admin,
            title="Test Post",
            description="Test content",
            category=Post.CATEGORY_SUGGESTION,
        )
        self.client.login(email="admin@example.com", password="StrongPass123")

        response = self.client.get(reverse("dashboard:posts"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Post")

    def test_admin_can_edit_post(self):
        post = Post.objects.create(
            author=self.admin,
            title="Test Post",
            description="Test content",
            category=Post.CATEGORY_SUGGESTION,
        )
        self.client.login(email="admin@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("dashboard:post_edit", args=[post.pk]),
            {
                "title": "Updated Title",
                "description": "Test content",
                "category": Post.CATEGORY_SUGGESTION,
                "status": Post.STATUS_APPROVED,
                "admin_status": Post.ADMIN_STATUS_PLANNED,
            },
        )

        self.assertEqual(response.status_code, 302)
        post.refresh_from_db()
        self.assertEqual(post.title, "Updated Title")
        self.assertEqual(post.admin_status, Post.ADMIN_STATUS_PLANNED)

    def test_non_admin_cannot_access_posts(self):
        user = get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("dashboard:posts"))

        self.assertEqual(response.status_code, 403)