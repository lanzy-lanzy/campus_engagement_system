from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from accounts.models import Friendship
from .forms import MessageForm
from .models import Conversation, Message


def _conversation_queryset(user):
    return (
        Conversation.objects.filter(participants=user)
        .prefetch_related("participants", "messages__sender")
        .annotate(last_message_at=Max("messages__created_at"))
        .order_by("-last_message_at", "-updated_at")
    )


def _people_queryset(user, query=""):
    people = get_user_model().objects.filter(is_active=True).exclude(pk=user.pk).order_by("username")
    if query:
        people = people.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(department__icontains=query))
    return people


def _chat_context(request, active_conversation=None, form=None):
    query = request.GET.get("q", "").strip()
    conversations = list(_conversation_queryset(request.user))
    conversation_items = [
        {
            "conversation": conversation,
            "person": conversation.other_participant(request.user),
            "last_message": conversation.last_message,
            "unread_count": conversation.messages.filter(read_at__isnull=True).exclude(sender=request.user).count(),
        }
        for conversation in conversations
    ]
    people = [
        {
            "user": person,
            "friendship_status": Friendship.status_for(request.user, person),
        }
        for person in _people_queryset(request.user, query)
    ]

    return {
        "conversations": conversations,
        "conversation_items": conversation_items,
        "people": people,
        "active_conversation": active_conversation,
        "active_person": active_conversation.other_participant(request.user) if active_conversation else None,
        "messages": active_conversation.messages.select_related("sender") if active_conversation else [],
        "form": form or MessageForm(),
        "query": query,
    }


def _get_participant_conversation(user, pk):
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related("participants").filter(participants=user),
        pk=pk,
    )
    return conversation


@login_required
def inbox(request):
    return render(request, "chat/inbox.html", _chat_context(request))


@login_required
def conversation_detail(request, pk):
    conversation = _get_participant_conversation(request.user, pk)
    conversation.messages.exclude(sender=request.user).filter(read_at__isnull=True).update(read_at=timezone.now())
    return render(request, "chat/inbox.html", _chat_context(request, conversation))


@login_required
def start_conversation(request, user_pk):
    other_user = get_object_or_404(get_user_model(), pk=user_pk, is_active=True)
    if other_user == request.user:
        raise Http404

    conversation = Conversation.between(request.user, other_user)
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(conversation=conversation, sender=request.user, body=form.cleaned_data["body"])
            conversation.touch()
    return redirect("chat:conversation", pk=conversation.pk)


@login_required
def send_message(request, pk):
    conversation = _get_participant_conversation(request.user, pk)
    form = MessageForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        Message.objects.create(conversation=conversation, sender=request.user, body=form.cleaned_data["body"])
        conversation.touch()
        form = MessageForm()

    if request.headers.get("HX-Request"):
        messages_html = render_to_string(
            "chat/partials/message_list.html",
            {"active_conversation": conversation, "messages": conversation.messages.select_related("sender")},
            request=request,
        )
        composer_html = render_to_string(
            "chat/partials/composer.html",
            {"active_conversation": conversation, "form": form, "oob": True},
            request=request,
        )
        return HttpResponse(messages_html + composer_html)

    return redirect("chat:conversation", pk=conversation.pk)
