from django.conf import settings
from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return f"Conversation {self.pk}"

    @classmethod
    def between(cls, user, other_user):
        conversations = cls.objects.filter(participants=user).filter(participants=other_user).distinct()
        for conversation in conversations:
            if conversation.participants.count() == 2:
                return conversation
        conversation = cls.objects.create()
        conversation.participants.add(user, other_user)
        return conversation

    def other_participant(self, user):
        return self.participants.exclude(pk=user.pk).first()

    @property
    def last_message(self):
        return self.messages.order_by("-created_at").first()

    def last_message_for(self, user):
        return self.messages.exclude(deleted_for=user).exclude(deleted_for_everyone=True).order_by("-created_at").first()

    def touch(self):
        self.updated_at = timezone.now()
        self.save(update_fields=["updated_at"])


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    body = models.TextField(max_length=1000)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_for_everyone = models.BooleanField(default=False)
    deleted_for = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="deleted_messages", blank=True)

    class Meta:
        ordering = ("created_at", "id")

    def __str__(self):
        return f"Message {self.pk} by {self.sender_id}"

    def mark_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=["read_at"])

    def is_deleted_for(self, user):
        if self.deleted_for_everyone:
            return True
        return self.deleted_for.filter(pk=user.pk).exists()

    def can_delete_for_everyone(self, user):
        from django.utils import timezone
        from datetime import timedelta
        return self.sender == user and (timezone.now() - self.created_at) < timedelta(minutes=10)
