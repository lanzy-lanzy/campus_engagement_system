from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "description", "category", "image")
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "description": forms.Textarea(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]", "rows": 5}),
            "category": forms.Select(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "image": forms.FileInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm file:mr-4 file:rounded file:border-0 file:bg-[#2C3E94] file:px-4 file:py-2 file:text-sm file:font-medium file:text-white"}),
        }