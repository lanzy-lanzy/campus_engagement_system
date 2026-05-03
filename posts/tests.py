import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from interactions.models import Comment, Reaction

from .models import Post, PostAttachment, PostTag


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
    @classmethod
    def setUpClass(cls):
        cls._media_root = tempfile.mkdtemp()
        cls._media_override = override_settings(MEDIA_ROOT=cls._media_root)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)

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

    def test_anonymous_feed_renders_pulsecampus_landing(self):
        response = self.client.get(reverse("posts:feed"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PulseCampus")
        self.assertContains(response, "Turn student voices into campus action.")
        self.assertContains(response, 'data-pulse-scene')
        self.assertContains(response, reverse("accounts:register"))
        self.assertNotContains(response, 'id="feed-composer"')

    def test_authenticated_feed_still_renders_feed(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("posts:feed"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="feed-composer"')
        self.assertContains(response, "PulseCampus")

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

    def test_feed_renders_inline_composer(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("posts:feed"))

        self.assertContains(response, 'id="feed-composer"')
        self.assertContains(response, 'hx-post="/posts/new/"')
        self.assertContains(response, 'hx-encoding="multipart/form-data"')
        self.assertContains(response, 'name="images"')
        self.assertContains(response, "multiple")
        self.assertContains(response, 'name="video"')
        self.assertContains(response, 'name="tags"')
        self.assertContains(response, "data-mentions")

    def test_htmx_create_post_accepts_up_to_five_images_and_one_video(self):
        self.client.login(email="student@example.com", password="StrongPass123")
        images = [
            SimpleUploadedFile(f"campus-{index}.jpg", b"image-bytes", content_type="image/jpeg")
            for index in range(5)
        ]
        video = SimpleUploadedFile("campus-tour.mp4", b"video-bytes", content_type="video/mp4")

        response = self.client.post(
            reverse("posts:create"),
            {
                "title": "Media rich update",
                "description": "Here are several views from the event.",
                "category": Post.CATEGORY_EVENT,
                "images": images,
                "video": video,
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(title="Media rich update")
        self.assertEqual(post.attachments.filter(media_type=PostAttachment.TYPE_IMAGE).count(), 5)
        self.assertEqual(post.attachments.filter(media_type=PostAttachment.TYPE_VIDEO).count(), 1)
        self.assertContains(response, "cv-media-carousel")
        self.assertContains(response, "<video")

    def test_create_post_rejects_more_than_five_images(self):
        self.client.login(email="student@example.com", password="StrongPass123")
        images = [
            SimpleUploadedFile(f"campus-{index}.jpg", b"image-bytes", content_type="image/jpeg")
            for index in range(6)
        ]

        response = self.client.post(
            reverse("posts:create"),
            {
                "title": "Too many photos",
                "description": "This should not save.",
                "category": Post.CATEGORY_EVENT,
                "images": images,
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Post.objects.filter(title="Too many photos").count(), 0)
        self.assertContains(response, "Upload up to 5 images", status_code=400)

    def test_htmx_create_post_stays_on_feed_and_prepends_post(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("posts:create"),
            {
                "title": "Inline campus update",
                "description": "This should appear without leaving the feed.",
                "category": Post.CATEGORY_SUGGESTION,
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.headers["HX-Retarget"], "#post-list")
        self.assertEqual(response.headers["HX-Reswap"], "afterbegin")
        self.assertContains(response, "Inline campus update")
        self.assertContains(response, 'hx-swap-oob="outerHTML"')

    def test_create_post_saves_normalized_tags_and_renders_them(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("posts:create"),
            {
                "title": "Safer evening paths",
                "description": "Add lights near the gym.",
                "category": Post.CATEGORY_IMPROVEMENT,
                "tags": "#Safety, campus lights,  student-life  ",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(title="Safer evening paths")
        self.assertEqual(
            list(post.tags.order_by("name").values_list("name", flat=True)),
            ["campus-lights", "safety", "student-life"],
        )
        self.assertEqual(PostTag.objects.count(), 3)
        self.assertContains(response, "#safety")
        self.assertContains(response, "#campus-lights")

    def test_feed_renders_share_action_for_posts(self):
        post = Post.objects.create(
            author=self.user,
            title="Library hours",
            description="Open earlier.",
            category=Post.CATEGORY_SUGGESTION,
            status=Post.STATUS_APPROVED,
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("posts:feed"))

        self.assertContains(response, f'hx-get="{reverse("posts:share", args=[post.pk])}"')
        self.assertContains(response, f'id="share-{post.pk}"')

    def test_post_modal_renders_post_actions_and_comments(self):
        post = Post.objects.create(
            author=self.user,
            title="Next.js Folder Structure",
            description="Understand project architecture at a glance.",
            category=Post.CATEGORY_SUGGESTION,
            status=Post.STATUS_APPROVED,
        )
        Comment.objects.create(post=post, author=self.user, body="gg")
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("posts:modal", args=[post.pk]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "student's Post")
        self.assertContains(response, "Next.js Folder Structure")
        self.assertContains(response, "Most relevant")
        self.assertContains(response, "gg")
        self.assertContains(response, 'id="post-modal"')
        self.assertNotContains(response, 'id="post-modal-root"')
        self.assertContains(response, "data-post-modal-backdrop")
        self.assertContains(response, "max-w-[630px]")
        self.assertContains(response, "modal-post-stats")
        self.assertContains(response, 'id="modal-comments-')
        self.assertContains(response, "/comments/?modal=1")
        self.assertContains(response, "/react/like/?modal=1")
        self.assertContains(response, f'hx-target="#modal-post-stats-{post.pk}"')
        self.assertContains(response, f'hx-target="#modal-share-{post.pk}"')
        self.assertNotContains(response, 'hx-swap-oob="true"')
        self.assertNotContains(response, "cv-react-btn")
        self.assertContains(response, "cv-comment-menu-button")
        self.assertContains(response, "document.getElementById('post-modal-root').innerHTML = ''")

    def test_feed_comment_action_targets_post_modal(self):
        post = Post.objects.create(
            author=self.user,
            title="Open comments in modal",
            description="The feed should stay clean.",
            category=Post.CATEGORY_SUGGESTION,
            status=Post.STATUS_APPROVED,
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("posts:feed"))

        self.assertContains(response, 'id="post-modal-root"')
        self.assertContains(response, f'hx-get="{reverse("posts:modal", args=[post.pk])}"')
        self.assertContains(response, 'hx-target="#post-modal-root"')
        self.assertContains(response, 'hx-swap="innerHTML"')

    def test_feed_footer_uses_single_compact_action_strip(self):
        post = Post.objects.create(
            author=self.user,
            title="Compact actions",
            description="Footer should not duplicate action rows.",
            category=Post.CATEGORY_SUGGESTION,
            status=Post.STATUS_APPROVED,
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("posts:feed"))

        self.assertContains(response, f'id="post-stats-{post.pk}"')
        self.assertContains(response, f'hx-post="{reverse("interactions:toggle_reaction", args=[post.pk, "like"])}"')
        self.assertContains(response, f'hx-target="#post-stats-{post.pk}"')
        self.assertContains(response, f'hx-get="{reverse("posts:modal", args=[post.pk])}"')
        self.assertContains(response, f'hx-get="{reverse("posts:share", args=[post.pk])}"')
        self.assertContains(response, f'hx-target="#share-{post.pk}"')
        self.assertNotContains(response, "cv-react-btn")

    def test_feed_can_auto_open_post_modal_from_notification_link(self):
        post = Post.objects.create(
            author=self.user,
            title="Open from notification",
            description="Notification links should show the post viewer.",
            category=Post.CATEGORY_SUGGESTION,
            status=Post.STATUS_APPROVED,
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(f"{reverse('posts:feed')}?post={post.pk}")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'id="post-{post.pk}"')
        self.assertContains(response, f'hx-get="{reverse("posts:modal", args=[post.pk])}"')
        self.assertContains(response, 'hx-trigger="load"')
        self.assertContains(response, 'hx-target="#post-modal-root"')

    def test_share_form_renders_for_htmx(self):
        post = Post.objects.create(
            author=self.user,
            title="Library hours",
            description="Open earlier.",
            category=Post.CATEGORY_SUGGESTION,
            status=Post.STATUS_APPROVED,
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("posts:share", args=[post.pk]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Share this post")
        self.assertContains(response, 'name="caption"')
        self.assertContains(response, post.title)

    def test_modal_share_form_targets_modal_slot(self):
        post = Post.objects.create(
            author=self.user,
            title="Library hours",
            description="Open earlier.",
            category=Post.CATEGORY_SUGGESTION,
            status=Post.STATUS_APPROVED,
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        modal_response = self.client.get(reverse("posts:modal", args=[post.pk]), HTTP_HX_REQUEST="true")
        response = self.client.get(f"{reverse('posts:share', args=[post.pk])}?modal=1", HTTP_HX_REQUEST="true")

        self.assertContains(modal_response, f'id="modal-share-{post.pk}"')
        self.assertContains(modal_response, f'hx-get="{reverse("posts:share", args=[post.pk])}?modal=1"')
        self.assertContains(modal_response, f'hx-target="#modal-share-{post.pk}"')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'id="modal-share-{post.pk}"')
        self.assertContains(response, f'hx-post="{reverse("posts:share", args=[post.pk])}?modal=1"')
        self.assertContains(response, f'hx-target="#modal-share-{post.pk}"')
        self.assertContains(response, f"document.getElementById('modal-share-{post.pk}').innerHTML = ''")
        self.assertNotContains(response, f'id="share-{post.pk}"')

    def test_modal_share_post_updates_modal_slot_without_feed_retarget(self):
        original_author = get_user_model().objects.create_user(
            username="origin",
            email="origin@example.com",
            password="StrongPass123",
        )
        original = Post.objects.create(
            author=original_author,
            title="Library hours",
            description="Open earlier.",
            category=Post.CATEGORY_SUGGESTION,
            status=Post.STATUS_APPROVED,
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            f"{reverse('posts:share', args=[original.pk])}?modal=1",
            {"caption": "This would help night classes too."},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 2)
        self.assertNotIn("HX-Retarget", response.headers)
        self.assertNotIn("HX-Reswap", response.headers)
        self.assertContains(response, f'id="modal-share-{original.pk}"')
        self.assertContains(response, f'id="modal-post-stats-{original.pk}"')
        self.assertContains(response, "1 share")
        self.assertContains(response, 'hx-swap-oob="outerHTML"')
        self.assertNotContains(response, "shared a post")

    def test_htmx_share_post_creates_feed_story_with_original_preview(self):
        original_author = get_user_model().objects.create_user(
            username="origin",
            email="origin@example.com",
            password="StrongPass123",
        )
        original = Post.objects.create(
            author=original_author,
            title="Library hours",
            description="Open earlier.",
            category=Post.CATEGORY_SUGGESTION,
            status=Post.STATUS_APPROVED,
        )
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("posts:share", args=[original.pk]),
            {"caption": "This would help night classes too."},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 2)
        shared_post = Post.objects.exclude(pk=original.pk).get()
        self.assertEqual(shared_post.author, self.user)
        self.assertEqual(shared_post.shared_from, original)
        self.assertEqual(shared_post.description, "This would help night classes too.")
        self.assertEqual(shared_post.category, original.category)
        self.assertEqual(response.headers["HX-Retarget"], "#post-list")
        self.assertEqual(response.headers["HX-Reswap"], "afterbegin")
        self.assertContains(response, "shared a post")
        self.assertContains(response, "This would help night classes too.")
        self.assertContains(response, "Library hours")
        self.assertContains(response, 'hx-swap-oob="outerHTML"')

    def test_sharing_a_shared_post_reuses_original_source(self):
        original_author = get_user_model().objects.create_user(
            username="origin",
            email="origin@example.com",
            password="StrongPass123",
        )
        original = Post.objects.create(
            author=original_author,
            title="Library hours",
            description="Open earlier.",
            category=Post.CATEGORY_SUGGESTION,
            status=Post.STATUS_APPROVED,
        )
        first_share = Post.objects.create(
            author=self.user,
            title="Shared: Library hours",
            description="First share.",
            category=Post.CATEGORY_SUGGESTION,
            status=Post.STATUS_APPROVED,
            shared_from=original,
        )
        another_user = get_user_model().objects.create_user(
            username="resharer",
            email="resharer@example.com",
            password="StrongPass123",
        )
        self.client.login(email="resharer@example.com", password="StrongPass123")

        response = self.client.post(
            reverse("posts:share", args=[first_share.pk]),
            {"caption": "Sharing this again."},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        new_share = Post.objects.exclude(pk__in=[original.pk, first_share.pk]).get()
        self.assertEqual(new_share.shared_from, original)


class FeedSidebarTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Improve library lighting",
            description="The second floor gets dim after 5 PM.",
            category=Post.CATEGORY_IMPROVEMENT,
        )
        self.trending_post = Post.objects.create(
            author=self.user,
            title="Add more water stations",
            description="The gym side needs refill stations.",
            category=Post.CATEGORY_SUGGESTION,
        )
        Comment.objects.create(post=self.post, author=self.user, body="I agree.")
        Reaction.objects.create(post=self.trending_post, user=self.user, kind=Reaction.KIND_LIKE)

    def test_feed_context_includes_sidebar_metrics(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("posts:feed"))

        self.assertEqual(response.status_code, 200)
        sidebar = response.context["feed_sidebar"]
        self.assertEqual(sidebar["approved_post_count"], 2)
        self.assertEqual(sidebar["visible_comment_count"], 1)
        self.assertEqual(sidebar["post_reaction_count"], 1)
        self.assertEqual(list(sidebar["trending_posts"]), [self.trending_post, self.post])

    def test_feed_renders_left_and_right_rail_content(self):
        self.client.login(email="student@example.com", password="StrongPass123")

        response = self.client.get(reverse("posts:feed"))

        self.assertContains(response, "cv-page-wide")
        self.assertContains(response, "cv-feed-shell")
        self.assertContains(response, "Feed shortcuts")
        self.assertContains(response, "Campus Activity")
        self.assertContains(response, "Trending Now")
        self.assertContains(response, "Posting Guide")
        self.assertContains(response, "Admin Status")
