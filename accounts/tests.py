from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Friendship


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


class AuthFlowTests(TestCase):
    def test_register_renders_pulsecampus_branding(self):
        response = self.client.get(reverse("accounts:register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PulseCampus")
        self.assertContains(response, "Turn student voices into campus action.")
        self.assertContains(response, 'data-pulse-scene')
        self.assertContains(response, "Create your student account")

    def test_admin_login_redirects_to_dashboard(self):
        user = get_user_model().objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="StrongPass123",
            role="admin",
            is_staff=True,
        )

        login_successful = self.client.login(email=user.email, password="StrongPass123")
        self.assertTrue(login_successful)
        response = self.client.get(reverse("accounts:post_login_redirect"))

        self.assertRedirects(response, reverse("dashboard:index"))


class FriendSearchTests(TestCase):
    def test_friend_search_returns_custom_user_display_data(self):
        User = get_user_model()
        student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
        )
        friend = User.objects.create_user(
            username="lanzy",
            email="lanzy@example.com",
            password="StrongPass123",
            department="Engineering",
        )
        Friendship.objects.create(
            requester=student,
            addressee=friend,
            status=Friendship.STATUS_ACCEPTED,
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("accounts:search_friends"), {"q": "lanzy"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "id": friend.pk,
                    "username": "lanzy",
                    "display_name": "lanzy",
                    "department": "Engineering",
                    "avatar_url": "",
                }
            ],
        )
