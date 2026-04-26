from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ("email", "username", "student_id", "department", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ""
        self.fields['username'].label = "Username"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.ROLE_STUDENT
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["username"]
        user.student_id = self.cleaned_data.get("student_id", "")
        user.department = self.cleaned_data.get("department", "")
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "username", "student_id", "department", "avatar", "bio")