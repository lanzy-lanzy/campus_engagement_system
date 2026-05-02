from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Friendship
from interactions.models import Comment, Reaction
from notifications.models import Mention, Notification
from posts.models import Post


class NotificationFeatureTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="StrongPass123",
        )
        self.friend = User.objects.create_user(
            username="friend",
            email="friend@example.com",
            password="StrongPass123",
        )
        self.stranger = User.objects.create_user(
            username="stranger",
            email="stranger@example.com",
            password="StrongPass123",
        )
        Friendship.objects.create(
            requester=self.author,
            addressee=self.friend,
            status=Friendship.STATUS_ACCEPTED,
        )

    def test_post_mentions_only_notify_accepted_friends(self):
        self.client.login(email="author@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("posts:create"),
            {
                "title": "Mention test",
                "description": "Thanks @friend and @stranger for the help.",
                "category": Post.CATEGORY_SUGGESTION,
            },
        )

        self.assertRedirects(response, reverse("posts:feed"))
        post = Post.objects.get(title="Mention test")
        self.assertEqual(Mention.objects.filter(post=post, recipient=self.friend).count(), 1)
        self.assertEqual(Mention.objects.filter(post=post, recipient=self.stranger).count(), 0)
        notification = Notification.objects.get(recipient=self.friend)
        self.assertEqual(notification.kind, Notification.KIND_MENTION_POST)
        self.assertEqual(notification.post, post)

    def test_comment_mention_notifies_friend_and_renders_highlight(self):
        post = Post.objects.create(
            author=self.stranger,
            title="Campus event",
            description="Join us.",
            category=Post.CATEGORY_EVENT,
        )
        self.client.login(email="author@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("interactions:add_comment", args=[post.pk]),
            {"body": "Looping in @friend and @stranger", "parent": ""},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get()
        self.assertEqual(Mention.objects.filter(comment=comment, recipient=self.friend).count(), 1)
        self.assertEqual(Mention.objects.filter(comment=comment, recipient=self.stranger).count(), 0)
        self.assertEqual(Notification.objects.filter(recipient=self.friend, kind=Notification.KIND_MENTION_COMMENT).count(), 1)
        self.assertContains(response, 'class="cv-mention"')
        self.assertContains(response, "@friend")

    def test_post_owner_gets_notifications_for_reaction_comment_and_share(self):
        post = Post.objects.create(
            author=self.author,
            title="Library hours",
            description="Open earlier.",
            category=Post.CATEGORY_SUGGESTION,
        )
        self.client.login(email="friend@example.com", password="StrongPass123")

        self.client.post(reverse("interactions:toggle_reaction", args=[post.pk, Reaction.KIND_LIKE]), HTTP_HX_REQUEST="true")
        self.client.post(
            reverse("interactions:add_comment", args=[post.pk]),
            {"body": "I agree.", "parent": ""},
            HTTP_HX_REQUEST="true",
        )
        self.client.post(
            reverse("posts:share", args=[post.pk]),
            {"caption": "Sharing this."},
            HTTP_HX_REQUEST="true",
        )

        kinds = set(Notification.objects.filter(recipient=self.author).values_list("kind", flat=True))
        self.assertIn(Notification.KIND_REACTION_POST, kinds)
        self.assertIn(Notification.KIND_COMMENT_POST, kinds)
        self.assertIn(Notification.KIND_SHARE_POST, kinds)

    def test_notifications_page_lists_and_marks_notifications_read(self):
        notification = Notification.objects.create(
            recipient=self.friend,
            actor=self.author,
            kind=Notification.KIND_MENTION_POST,
            post=Post.objects.create(
                author=self.author,
                title="Mention test",
                description="Hi @friend",
                category=Post.CATEGORY_SUGGESTION,
            ),
        )
        self.client.login(email="friend@example.com", password="StrongPass123")

        response = self.client.get(reverse("notifications:inbox"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "mentioned you in a post")
        notification.refresh_from_db()
        self.assertIsNotNone(notification.read_at)
