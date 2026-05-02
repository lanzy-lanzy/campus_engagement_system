import re

from django.contrib.auth import get_user_model

from accounts.models import Friendship

from .models import Mention, Notification


MENTION_RE = re.compile(r"(?<![\w@])@([A-Za-z0-9_]{1,150})")


def create_notification(recipient, actor, kind, post=None, comment=None):
    if not recipient or not actor or recipient.pk == actor.pk:
        return None
    notification, _ = Notification.objects.get_or_create(
        recipient=recipient,
        actor=actor,
        kind=kind,
        post=post,
        comment=comment,
    )
    return notification


def process_mentions(actor, text, post=None, comment=None):
    usernames = list(dict.fromkeys(MENTION_RE.findall(text or "")))
    if post:
        Mention.objects.filter(post=post).delete()
    if comment:
        Mention.objects.filter(comment=comment).delete()
    if not usernames:
        return []

    users = get_user_model().objects.filter(username__in=usernames, is_active=True)
    mentions = []
    for user in users:
        if Friendship.are_friends(actor, user):
            mention, _ = Mention.objects.get_or_create(
                recipient=user,
                actor=actor,
                post=post,
                comment=comment,
            )
            mentions.append(mention)
            create_notification(
                recipient=user,
                actor=actor,
                kind=Notification.KIND_MENTION_POST if post else Notification.KIND_MENTION_COMMENT,
                post=post or (comment.post if comment else None),
                comment=comment,
            )
    return mentions


def notify_post_reaction(post, actor):
    return create_notification(post.author, actor, Notification.KIND_REACTION_POST, post=post)


def notify_post_comment(post, comment):
    return create_notification(post.author, comment.author, Notification.KIND_COMMENT_POST, post=post, comment=comment)


def notify_post_share(source_post, actor):
    return create_notification(source_post.author, actor, Notification.KIND_SHARE_POST, post=source_post)


def notify_friend_request(requester, addressee):
    return create_notification(addressee, requester, Notification.KIND_FRIEND_REQUEST)


def notify_friend_accepted(requester, addressee):
    return create_notification(requester, addressee, Notification.KIND_FRIEND_ACCEPTED)
