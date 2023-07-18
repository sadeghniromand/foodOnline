from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from . import models


# custom Form for user register
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )


# use django user form for user register
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', ]
