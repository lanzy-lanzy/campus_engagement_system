from django import template
from interactions.models import Reaction

register = template.Library()

@register.filter
def user_liked(post, user):
    return post.user_has_reaction(user, 'like')

@register.filter
def user_hearted(post, user):
    return post.user_has_reaction(user, 'love')

@register.filter
def user_reaction(post, user):
    return post.get_user_reaction(user)

@register.filter
def reaction_counts(post):
    return post.get_reaction_counts()

@register.filter
def reaction_icon(kind):
    return Reaction.REACTION_ICONS.get(kind, '👍')

@register.filter
def get_comment_reaction(comment, user):
    if not user or not user.is_authenticated:
        return None
    reaction = comment.reactions.filter(user=user).first()
    return reaction.kind if reaction else None

@register.filter
def get_comment_reaction_counts(comment):
    counts = {}
    for kind, label in Reaction.KIND_CHOICES:
        counts[kind] = comment.reactions.filter(kind=kind).count()
    return counts

@register.filter
def total_reactions(counts):
    return sum(counts.values())

@register.filter
def comment_replies_count(comment):
    return comment.replies.filter(status="visible").count()