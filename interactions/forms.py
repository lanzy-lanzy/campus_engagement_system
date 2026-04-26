from django import forms

from .models import Comment, Report


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body", "parent")
        widgets = {
            "body": forms.Textarea(attrs={"rows": 2, "placeholder": "Write a comment"}),
            "parent": forms.HiddenInput(),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("reason", "details")
        widgets = {
            "details": forms.Textarea(attrs={"rows": 3, "placeholder": "Add helpful context"}),
        }