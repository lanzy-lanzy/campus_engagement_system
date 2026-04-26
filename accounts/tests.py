from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserModelTests(TestCase):
    def test_student_user_defaults_to_student_role(self):
        user = get_user_model().objects.create_user(
            username="ana",
            email="ana@example.com",
            password="StrongPass123",
        )

        self.assertEqual(user.role, "student")
        self.assertTrue(user.is_student)
        self.assertFalse(user.is_campus_admin)

    def test_superuser_is_admin_role(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
        )

        self.assertEqual(user.role, "admin")
        self.assertTrue(user.is_campus_admin)

    def test_superuser_rejects_student_role(self):
        with self.assertRaisesMessage(ValueError, "Superuser must have role of admin."):
            get_user_model().objects.create_superuser(
                username="student-admin",
                email="student-admin@example.com",
                password="StrongPass123",
                role="student",
            )


class AuthFlowTests(TestCase):
    def test_register_creates_student_and_redirects_to_feed(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "mika",
                "email": "mika@example.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "student_id": "2026-001",
                "department": "Engineering",
            },
        )

        self.assertRedirects(response, reverse("posts:feed"))
        user = get_user_model().objects.get(username="mika")
        self.assertEqual(user.role, "student")

    def test_admin_login_redirects_to_dashboard(self):
        user = get_user_model().objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="StrongPass123",
            role="admin",
            is_staff=True,
        )

        self.client.login(username=user.username, password="StrongPass123")
        response = self.client.get(reverse("accounts:post_login_redirect"))

        self.assertRedirects(response, reverse("dashboard:index"))
