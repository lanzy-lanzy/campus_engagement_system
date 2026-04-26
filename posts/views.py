from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Post


@login_required
def feed(request):
    sort = request.GET.get("sort", "latest")
    posts = Post.objects.filter(status=Post.STATUS_APPROVED).select_related("author")

    if sort == "most_liked":
        posts = posts.annotate(likes=Count("reactions", filter=Q(reactions__kind="like"))).order_by("-likes", "-created_at")
    elif sort == "trending":
        posts = posts.annotate(
            likes=Count("reactions", filter=Q(reactions__kind="like")),
            hearts=Count("reactions", filter=Q(reactions__kind="heart")),
            comment_total=Count("comments"),
        ).order_by("-hearts", "-likes", "-comment_total", "-created_at")
    else:
        posts = posts.order_by("-created_at")

    context = {"posts": posts, "sort": sort, "form": PostForm()}
    template = "posts/partials/post_list.html" if request.headers.get("HX-Request") else "posts/feed.html"
    return render(request, template, context)


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:feed")
    else:
        form = PostForm()
    return render(request, "posts/post_form.html", {"form": form, "mode": "Create"})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_campus_admin:
        raise PermissionDenied
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
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