import re

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

MENTION_RE = re.compile(r"(?<![\w@])@([A-Za-z0-9_]{1,150})")


@register.filter(needs_autoescape=True)
def mentionize(text, target, autoescape=True):
    value = conditional_escape(text or "") if autoescape else (text or "")
    mentions = getattr(target, "mentions", None)
    if mentions is None:
        return mark_safe(value)

    usernames = set(mentions.select_related("recipient").values_list("recipient__username", flat=True))
    if not usernames:
        return mark_safe(value)

    def replace(match):
        username = match.group(1)
        mention = match.group(0)
        if username not in usernames:
            return mention
        return f'<span class="cv-mention">{mention}</span>'

    return mark_safe(MENTION_RE.sub(replace, value))
