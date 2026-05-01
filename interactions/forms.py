from django import forms

from .models import Comment, Report


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body", "parent")
        widgets = {
            "body": forms.Textarea(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]", "rows": 2, "placeholder": "Write a comment"}),
            "parent": forms.HiddenInput(),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("reason", "details")
        widgets = {
            "reason": forms.Select(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "details": forms.Textarea(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]", "rows": 3, "placeholder": "Add helpful context"}),
        }