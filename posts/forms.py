import re

from django import forms

from .models import Post, PostTag


TAG_SPLIT_RE = re.compile(r"[,\n]+")
TAG_CLEAN_RE = re.compile(r"[^a-z0-9-]+")


def normalize_tag(value):
    tag = TAG_CLEAN_RE.sub("-", (value or "").strip().lower().lstrip("#"))
    return tag.strip("-")


def parse_tags(value):
    tags = []
    seen = set()
    for raw_tag in TAG_SPLIT_RE.split(value or ""):
        tag = normalize_tag(raw_tag)
        if tag and tag not in seen:
            seen.add(tag)
            tags.append(tag)
    return tags[:8]


class PostForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]",
                "placeholder": "safety, library-hours, campus-life",
            }
        ),
    )

    class Meta:
        model = Post
        fields = ("title", "description", "category")
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]", "data-mentions": ""}),
            "description": forms.Textarea(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]", "rows": 5, "data-mentions": ""}),
            "category": forms.Select(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and "tags" not in self.initial:
            self.initial["tags"] = ", ".join(self.instance.tags.values_list("name", flat=True))

    def clean_tags(self):
        return parse_tags(self.cleaned_data.get("tags", ""))

    def save_tags(self, post):
        tag_names = self.cleaned_data.get("tags", [])
        tags = [PostTag.objects.get_or_create(name=name)[0] for name in tag_names]
        post.tags.set(tags)
