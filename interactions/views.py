from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone

from posts.models import Post
from notifications.services import notify_post_comment, notify_post_reaction, process_mentions

from .forms import CommentForm, ReportForm
from .models import Comment, Reaction, Report


def _htmx_error(request, message, status=400):
    html = render_to_string("interactions/partials/inline_error.html", {"message": message}, request=request)
    return HttpResponse(html, status=status)


def _is_modal_request(request):
    return request.GET.get("modal") == "1"


def _render_comment_list(request, post, status=200, in_modal=False):
    comments = post.comments.filter(parent__isnull=True, status=Comment.STATUS_VISIBLE).select_related("author").prefetch_related(
        "mentions__recipient",
        "replies__author",
        "replies__mentions__recipient",
        "replies__reactions",
        "reactions",
    )
    context = {"post": post, "comments": comments, "form": CommentForm(), "in_modal": in_modal}
    if in_modal:
        comments_html = render_to_string("interactions/partials/comment_list.html", context, request=request)
        modal_stats_html = render_to_string("interactions/partials/post_stats.html", {"post": post, "in_modal": True, "force_oob": True}, request=request)
        feed_stats_html = render_to_string("interactions/partials/post_stats.html", {"post": post, "force_oob": True}, request=request)
        return HttpResponse(comments_html + modal_stats_html + feed_stats_html, status=status)
    return render(request, "interactions/partials/comment_list.html", context, status=status)


@login_required
def toggle_reaction(request, post_id, kind):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    if kind not in [r[0] for r in Reaction.KIND_CHOICES]:
        return HttpResponseBadRequest("Unknown reaction")

    post = get_object_or_404(Post, pk=post_id, status=Post.STATUS_APPROVED)
    in_modal = _is_modal_request(request)

    reaction = Reaction.objects.filter(post=post, comment__isnull=True, user=request.user).first()
    if reaction and reaction.kind == kind:
        reaction.delete()
    elif reaction:
        reaction.kind = kind
        reaction.save(update_fields=["kind"])
        notify_post_reaction(post, request.user)
    else:
        Reaction.objects.create(post=post, user=request.user, kind=kind)
        notify_post_reaction(post, request.user)

    reaction_bar_html = render_to_string("interactions/partials/reaction_bar.html", {"post": post, "in_modal": in_modal}, request=request)
    post_stats_html = render_to_string("interactions/partials/post_stats.html", {"post": post, "in_modal": in_modal, "force_oob": in_modal}, request=request)
    if in_modal:
        feed_reaction_bar_html = render_to_string("interactions/partials/reaction_bar.html", {"post": post, "force_oob": True}, request=request)
        feed_post_stats_html = render_to_string("interactions/partials/post_stats.html", {"post": post, "force_oob": True}, request=request)
        return HttpResponse(reaction_bar_html + post_stats_html + feed_reaction_bar_html + feed_post_stats_html)
    return HttpResponse(reaction_bar_html + post_stats_html)


@login_required
def toggle_comment_reaction(request, comment_id, kind):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    if kind not in [r[0] for r in Reaction.KIND_CHOICES]:
        return HttpResponseBadRequest("Unknown reaction")

    comment = get_object_or_404(Comment, pk=comment_id)

    reaction = Reaction.objects.filter(comment=comment, user=request.user).first()
    if reaction and reaction.kind == kind:
        reaction.delete()
    elif reaction:
        reaction.kind = kind
        reaction.save(update_fields=["kind"])
    else:
        Reaction.objects.create(comment=comment, user=request.user, kind=kind)

    return render(request, "interactions/partials/comment_actions.html", {"comment": comment, "post": comment.post})


@login_required
def hide_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    post = comment.post
    if post.author != request.user and not request.user.is_campus_admin:
        raise PermissionDenied
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    comment.status = Comment.STATUS_HIDDEN
    comment.save(update_fields=["status"])
    return _render_comment_list(request, post, in_modal=_is_modal_request(request))


@login_required
def add_reply(request, comment_id):
    parent_comment = get_object_or_404(Comment, pk=comment_id)
    post = parent_comment.post
    in_modal = _is_modal_request(request)
    if request.method != "POST":
        form = CommentForm()
        return render(request, "interactions/partials/reply_form.html", {"comment": parent_comment, "form": form, "post": post, "in_modal": in_modal})

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.parent = parent_comment
        comment.save()
        process_mentions(request.user, comment.body, comment=comment)
        notify_post_comment(post, comment)
        form = CommentForm()
    return _render_comment_list(request, post, in_modal=in_modal)


@login_required
def get_reaction_bar(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, "interactions/partials/reaction_bar.html", {"post": post, "in_modal": _is_modal_request(request)})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id, status=Post.STATUS_APPROVED)
    in_modal = _is_modal_request(request)
    if request.method != "POST":
        form = CommentForm()
        return render(request, "interactions/partials/comment_form.html", {"post": post, "form": form, "in_modal": in_modal})

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        process_mentions(request.user, comment.body, comment=comment)
        notify_post_comment(post, comment)
        form = CommentForm()
    return _render_comment_list(request, post, in_modal=in_modal)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user and not request.user.is_campus_admin:
        raise PermissionDenied
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    post = comment.post
    comment.delete()
    return _render_comment_list(request, post, in_modal=_is_modal_request(request))


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment.objects.select_related("post", "author"), pk=comment_id)
    in_modal = _is_modal_request(request)
    if comment.author != request.user and not request.user.is_campus_admin:
        raise PermissionDenied

    if request.method != "POST":
        form = CommentForm(instance=comment)
        return render(request, "interactions/partials/comment_edit_form.html", {"comment": comment, "post": comment.post, "form": form, "in_modal": in_modal})

    form = CommentForm(request.POST, instance=comment)
    if form.is_valid():
        comment = form.save()
        process_mentions(request.user, comment.body, comment=comment)
        return _render_comment_list(request, comment.post, in_modal=in_modal)

    return render(
        request,
        "interactions/partials/comment_edit_form.html",
        {"comment": comment, "post": comment.post, "form": form, "in_modal": in_modal},
        status=400,
    )


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
