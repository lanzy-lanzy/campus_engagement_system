from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Friendship
from .models import Conversation, Message


class ChatViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
        )
        self.friend = User.objects.create_user(
            username="friend",
            email="friend@example.com",
            password="StrongPass123",
            department="Engineering",
        )
        self.other = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass123",
        )

    def test_chat_requires_login(self):
        response = self.client.get(reverse("chat:inbox"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_inbox_renders_people_and_empty_state(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("chat:inbox"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Messenger")
        self.assertContains(response, "friend")
        self.assertContains(response, "Engineering")
        self.assertContains(response, "Select a conversation")
        self.assertContains(response, reverse("chat:start", args=[self.friend.pk]))

    def test_inbox_renders_friend_actions(self):
        Friendship.objects.create(
            requester=self.student,
            addressee=self.friend,
            status=Friendship.STATUS_ACCEPTED,
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("chat:inbox"))

        self.assertContains(response, "Friends")
        self.assertContains(response, "Add Friend")

    def test_sending_message_creates_one_to_one_conversation(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("chat:start", args=[self.friend.pk]),
            {"body": "Hey, are you on campus?"},
        )

        self.assertEqual(response.status_code, 302)
        conversation = Conversation.objects.get()
        self.assertEqual(set(conversation.participants.all()), {self.student, self.friend})
        self.assertEqual(Message.objects.get().body, "Hey, are you on campus?")
        self.assertRedirects(response, reverse("chat:conversation", args=[conversation.pk]))

    def test_sending_message_reuses_existing_conversation(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.student, self.friend)
        self.client.login(email="student@example.com", password="StrongPass123")

        self.client.post(reverse("chat:start", args=[self.friend.pk]), {"body": "First"})
        self.client.post(reverse("chat:start", args=[self.friend.pk]), {"body": "Second"})

        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(conversation.messages.count(), 2)

    def test_conversation_view_only_allows_participants(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.student, self.friend)
        self.client.login(email="other@example.com", password="StrongPass123")

        response = self.client.get(reverse("chat:conversation", args=[conversation.pk]))

        self.assertEqual(response.status_code, 404)

    def test_htmx_send_message_returns_message_list_and_composer(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.student, self.friend)
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("chat:send", args=[conversation.pk]),
            {"body": "This should appear instantly."},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(conversation.messages.count(), 1)
        self.assertContains(response, "This should appear instantly.")
        self.assertContains(response, 'id="chat-composer"')
        self.assertContains(response, 'hx-swap-oob="outerHTML"')

    def test_unread_messages_show_topnav_and_conversation_badges(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.student, self.friend)
        Message.objects.create(
            conversation=conversation,
            sender=self.friend,
            body="Unread ping",
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("chat:inbox"))

        self.assertContains(response, 'data-badge="messenger"')
        self.assertContains(response, "Unread ping")
        self.assertContains(response, 'class="cv-unread-dot"')
