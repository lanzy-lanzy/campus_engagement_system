from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Post


@login_required
def feed(request):
    sort = request.GET.get("sort", "latest")
    query = request.GET.get("q", "")
    category = request.GET.get("category", "")
    page = request.GET.get("page", 1)
    posts = Post.objects.filter(status=Post.STATUS_APPROVED).select_related("author")

    if query:
        posts = posts.filter(models.Q(title__icontains=query) | models.Q(description__icontains=query))

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

    context = {
        "posts": page_obj.object_list,
        "sort": sort,
        "form": PostForm(),
        "query": query,
        "category": category,
        "page_obj": page_obj,
        "categories": Post.CATEGORY_CHOICES,
    }

    if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
        return render(request, "posts/partials/post_list.html", context)

    return render(request, "posts/feed.html", context)


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
