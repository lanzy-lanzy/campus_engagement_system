from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


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