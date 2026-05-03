from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from interactions.models import Comment, Reaction
from notifications.services import notify_post_share, process_mentions

from .forms import PostForm
from .models import Post, PostAttachment


MAX_POST_IMAGES = 5
MAX_POST_VIDEOS = 1


def _get_uploaded_images(files):
    images = list(files.getlist("images"))
    legacy_image = files.get("image")
    if legacy_image:
        images.append(legacy_image)
    return images


def _get_uploaded_video(files):
    return files.get("video")


def _file_matches_type(uploaded_file, media_prefix):
    content_type = getattr(uploaded_file, "content_type", "") or ""
    return content_type.startswith(media_prefix)


def _validate_post_media(form, files, post=None):
    images = _get_uploaded_images(files)
    video = _get_uploaded_video(files)
    existing_images = 0
    existing_videos = 0

    if post:
        existing_images = post.attachments.filter(media_type=PostAttachment.TYPE_IMAGE).count()
        existing_videos = post.attachments.filter(media_type=PostAttachment.TYPE_VIDEO).count()

    if existing_images + len(images) > MAX_POST_IMAGES:
        form.add_error(None, f"Upload up to {MAX_POST_IMAGES} images per post.")

    if existing_videos + (1 if video else 0) > MAX_POST_VIDEOS:
        form.add_error(None, "Upload only 1 video per post.")

    for image in images:
        if not _file_matches_type(image, "image/"):
            form.add_error(None, "Images must use an image file type.")
            break

    if video and not _file_matches_type(video, "video/"):
        form.add_error(None, "Video must use a video file type.")

    return not form.errors


def _save_post_media(post, files):
    next_position = post.attachments.count()

    for image in _get_uploaded_images(files):
        PostAttachment.objects.create(
            post=post,
            file=image,
            media_type=PostAttachment.TYPE_IMAGE,
            position=next_position,
        )
        next_position += 1

    video = _get_uploaded_video(files)
    if video:
        PostAttachment.objects.create(
            post=post,
            file=video,
            media_type=PostAttachment.TYPE_VIDEO,
            position=next_position,
        )


def feed(request):
    if not request.user.is_authenticated:
        return render(request, "landing.html")

    sort = request.GET.get("sort", "latest")
    query = request.GET.get("q", "")
    category = request.GET.get("category", "")
    page = request.GET.get("page", 1)
    open_post_id = request.GET.get("post", "")
    posts = Post.objects.filter(status=Post.STATUS_APPROVED).select_related("author", "shared_from__author").prefetch_related(
        "attachments",
        "shared_from__attachments",
        "mentions__recipient",
        "comments__mentions__recipient",
        "tags",
    )

    if query:
        posts = posts.filter(models.Q(title__icontains=query) | models.Q(description__icontains=query) | models.Q(tags__name__icontains=query)).distinct()

    if category:
        posts = posts.filter(category=category)

    if sort == "most_liked":
        posts = posts.annotate(likes=Count("reactions")).order_by("-likes", "-created_at")
    elif sort == "trending":
        posts = posts.annotate(
            total_reactions=Count("reactions"),
            comment_total=Count("comments"),
        ).order_by("-total_reactions", "-comment_total", "-created_at")
    else:
        posts = posts.order_by("-created_at")

    paginator = Paginator(posts, 5)  # Smaller page size for better infinite scroll demo
    page_obj = paginator.get_page(page)

    sidebar_posts = Post.objects.filter(status=Post.STATUS_APPROVED).select_related("author", "shared_from__author").prefetch_related(
        "attachments",
        "shared_from__attachments",
    )
    trending_posts = sidebar_posts.annotate(
        reaction_total=Count("reactions", filter=Q(reactions__comment__isnull=True), distinct=True),
        comment_total=Count("comments", filter=Q(comments__status="visible", comments__parent__isnull=True), distinct=True),
    ).order_by("-reaction_total", "-comment_total", "-created_at")[:3]

    feed_sidebar = {
        "approved_post_count": sidebar_posts.count(),
        "visible_comment_count": Comment.objects.filter(
            status=Comment.STATUS_VISIBLE,
            parent__isnull=True,
            post__status=Post.STATUS_APPROVED,
        ).count(),
        "post_reaction_count": Reaction.objects.filter(
            post__status=Post.STATUS_APPROVED,
            comment__isnull=True,
        ).count(),
        "trending_posts": trending_posts,
    }

    context = {
        "posts": page_obj.object_list,
        "sort": sort,
        "form": PostForm(),
        "query": query,
        "category": category,
        "page_obj": page_obj,
        "categories": Post.CATEGORY_CHOICES,
        "feed_sidebar": feed_sidebar,
        "open_post_id": open_post_id if open_post_id and Post.objects.filter(pk=open_post_id, status=Post.STATUS_APPROVED).exists() else "",
    }

    if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
        return render(request, "posts/partials/post_list.html", context)

    return render(request, "posts/feed.html", context)


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        media_is_valid = _validate_post_media(form, request.FILES)
        if form.is_valid() and media_is_valid:
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_tags(post)
            _save_post_media(post, request.FILES)
            process_mentions(request.user, f"{post.title} {post.description}", post=post)
            if request.headers.get("HX-Request"):
                post_html = render_to_string("posts/partials/post_card.html", {"post": post}, request=request)
                composer_html = render_to_string("posts/partials/inline_composer.html", {"form": PostForm(), "oob": True}, request=request)
                response = HttpResponse(post_html + composer_html)
                response["HX-Retarget"] = "#post-list"
                response["HX-Reswap"] = "afterbegin"
                return response
            return redirect("posts:feed")
        if request.headers.get("HX-Request"):
            return render(request, "posts/partials/inline_composer.html", {"form": form}, status=400)
    else:
        form = PostForm()
    return render(request, "posts/post_form.html", {"form": form, "mode": "Create"})


@login_required
def create_post_modal(request):
    form = PostForm()
    return render(request, "posts/partials/create_post_modal.html", {"form": form})


@login_required
def share_post(request, pk):
    post = get_object_or_404(Post.objects.select_related("author", "shared_from__author"), pk=pk, status=Post.STATUS_APPROVED)
    source = post.share_source
    if request.method != "POST":
        return render(request, "posts/partials/share_form.html", {"post": post, "source": source})

    caption = request.POST.get("caption", "").strip()
    shared_post = Post.objects.create(
        author=request.user,
        title=f"Shared: {source.title}"[:180],
        description=caption,
        category=source.category,
        image=None,
        status=Post.STATUS_APPROVED,
        admin_status=Post.ADMIN_STATUS_NONE,
        shared_from=source,
        shared_at=timezone.now(),
    )
    notify_post_share(source, request.user)

    if request.headers.get("HX-Request"):
        post_html = render_to_string("posts/partials/post_card.html", {"post": shared_post}, request=request)
        share_slot_html = render_to_string("posts/partials/share_slot.html", {"post": post, "oob": True}, request=request)
        response = HttpResponse(post_html + share_slot_html)
        response["HX-Retarget"] = "#post-list"
        response["HX-Reswap"] = "afterbegin"
        return response
    return redirect("posts:feed")


@login_required
def post_modal(request, pk):
    post = get_object_or_404(
        Post.objects.filter(status=Post.STATUS_APPROVED)
        .select_related("author", "shared_from__author")
        .prefetch_related(
            "attachments",
            "shared_from__attachments",
            "mentions__recipient",
            "comments__author",
            "comments__mentions__recipient",
            "comments__reactions",
            "comments__replies__author",
            "comments__replies__mentions__recipient",
            "comments__replies__reactions",
            "tags",
        ),
        pk=pk,
    )
    comments = post.comments.filter(parent__isnull=True, status=Comment.STATUS_VISIBLE).select_related("author").prefetch_related(
        "mentions__recipient",
        "replies__author",
        "replies__mentions__recipient",
        "replies__reactions",
        "reactions",
    )
    return render(request, "posts/partials/post_modal.html", {"post": post, "comments": comments})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post.objects.prefetch_related("attachments"), pk=pk)
    if post.author != request.user and not request.user.is_campus_admin:
        raise PermissionDenied
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        media_is_valid = _validate_post_media(form, request.FILES, post=post)
        if form.is_valid() and media_is_valid:
            post = form.save()
            form.save_tags(post)
            _save_post_media(post, request.FILES)
            process_mentions(request.user, f"{post.title} {post.description}", post=post)
            return redirect("posts:feed")
    else:
        form = PostForm(instance=post)
    return render(request, "posts/post_form.html", {"form": form, "mode": "Edit", "post": post})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_campus_admin:
        raise PermissionDenied
    if request.method == "POST":
        post.delete()
        if request.headers.get("HX-Request"):
            return render(request, "posts/partials/post_list.html", {"posts": Post.objects.filter(status=Post.STATUS_APPROVED)})
        return redirect("posts:feed")
    return render(request, "posts/post_confirm_delete.html", {"post": post})
