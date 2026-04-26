from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone

from posts.models import Post

from .forms import CommentForm, ReportForm
from .models import Comment, Reaction, Report


def _htmx_error(request, message, status=400):
    html = render_to_string("interactions/partials/inline_error.html", {"message": message}, request=request)
    return HttpResponse(html, status=status)


@login_required
def toggle_reaction(request, post_id, kind):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    if kind not in [Reaction.KIND_LIKE, Reaction.KIND_HEART]:
        return HttpResponseBadRequest("Unknown reaction")

    post = get_object_or_404(Post, pk=post_id, status=Post.STATUS_APPROVED)
    reaction, created = Reaction.objects.get_or_create(post=post, user=request.user, kind=kind)
    if not created:
        reaction.delete()
    return render(request, "interactions/partials/reaction_bar.html", {"post": post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id, status=Post.STATUS_APPROVED)
    if request.method != "POST":
        form = CommentForm()
        return render(request, "interactions/partials/comment_form.html", {"post": post, "form": form})

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        form = CommentForm()
    comments = post.comments.filter(parent__isnull=True, status=Comment.STATUS_VISIBLE).select_related("author")
    return render(request, "interactions/partials/comment_list.html", {"post": post, "comments": comments, "form": form})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user and not request.user.is_campus_admin:
        raise PermissionDenied
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    post = comment.post
    comment.delete()
    comments = post.comments.filter(parent__isnull=True, status=Comment.STATUS_VISIBLE).select_related("author")
    return render(request, "interactions/partials/comment_list.html", {"post": post, "comments": comments, "form": CommentForm()})


@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method != "POST":
        return render(request, "interactions/partials/report_form.html", {"post": post, "form": ReportForm()})

    form = ReportForm(request.POST)
    if form.is_valid():
        report = form.save(commit=False)
        report.post = post
        report.reporter = request.user
        report.save()
        return render(request, "interactions/partials/inline_error.html", {"message": "Report submitted."})
    return render(request, "interactions/partials/report_form.html", {"post": post, "form": form}, status=400)


@login_required
def resolve_report(request, report_id, status):
    if not request.user.is_campus_admin:
        raise PermissionDenied
    if status not in [Report.STATUS_RESOLVED, Report.STATUS_DISMISSED]:
        return HttpResponseBadRequest("Unknown status")
    report = get_object_or_404(Report, pk=report_id)
    report.status = status
    report.reviewed_by = request.user
    report.reviewed_at = timezone.now()
    report.save(update_fields=["status", "reviewed_by", "reviewed_at"])
    return render(request, "dashboard/partials/report_row.html", {"report": report})