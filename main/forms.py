from django import forms

from .models import CustomUser


class CustomUserRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password", "country")
