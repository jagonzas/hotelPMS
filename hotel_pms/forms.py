from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()  # if you want to add Email field
    user_type = forms.ChoiceField(choices=[('customer', 'Customer'), ('employee', 'Employee'), ('manager', 'Manager')])
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  # password1 is for creating password and password2 is for confirming the same password
