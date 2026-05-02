from django import forms

from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("body",)
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "class": "cv-chat-input",
                    "placeholder": "Message...",
                    "rows": 1,
                    "aria-label": "Message",
                }
            )
        }
