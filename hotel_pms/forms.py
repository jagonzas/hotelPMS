from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class GuestRegisterForm(UserCreationForm):
    email = forms.EmailField()  # if you want to add Email field
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  # password1 is for creating password and password2 is for confirming the same password



class StaffRegisterForm(UserCreationForm):
    staff_id = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'staff_id']