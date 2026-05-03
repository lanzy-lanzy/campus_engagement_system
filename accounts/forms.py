from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True, max_length=150)
    first_name = forms.CharField(required=True, max_length=150)
    last_name = forms.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "student_id", "department", "password1", "password2")
        widgets = {
            "email": forms.EmailInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "username": forms.TextInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "first_name": forms.TextInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "last_name": forms.TextInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "student_id": forms.TextInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "department": forms.TextInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "password1": forms.PasswordInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "password2": forms.PasswordInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ""
        self.fields['username'].label = "Username"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.ROLE_STUDENT
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["username"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.student_id = self.cleaned_data.get("student_id", "")
        user.department = self.cleaned_data.get("department", "")
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username", "student_id", "department", "avatar", "bio")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "last_name": forms.TextInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "email": forms.EmailInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "username": forms.TextInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "student_id": forms.TextInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "department": forms.TextInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]"}),
            "avatar": forms.FileInput(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm file:mr-4 file:rounded file:border-0 file:bg-[#2C3E94] file:px-4 file:py-2 file:text-sm file:font-medium file:text-white"}),
            "bio": forms.Textarea(attrs={"class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-[#2C3E94] focus:outline-none focus:ring-1 focus:ring-[#2C3E94]", "rows": 4}),
        }