from django import template

register = template.Library()


@register.filter
def message_deleted(message, user):
    return message.is_deleted_for(user)


@register.filter
def can_delete_everyone(message, user):
    return message.can_delete_for_everyone(user)