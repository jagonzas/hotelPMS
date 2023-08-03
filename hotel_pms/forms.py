from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Room, Customer, Booking


class CustomerRegisterForm(UserCreationForm):
    email = forms.EmailField()
    id_document = forms.FileField()  # for ID documents
    profile_picture = forms.ImageField(required=False)  # optional profile picture

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'id_document', 'profile_picture']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

        customer_profile = Customer(user=user, id_document=self.cleaned_data['id_document'], profile_picture=self.cleaned_data.get('profile_picture'))
        customer_profile.save()

        return user


class StaffRegisterForm(UserCreationForm):
    staff_id = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'staff_id']


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_type','rate', 'image']
        widgets = {
            'room_type': forms.Select(choices=Room.ROOM_TYPES),

            'rate': forms.NumberInput(attrs={'step': "0.01", 'min': "0"}),
            'image': forms.FileInput()
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.SelectDateWidget(),
            'end_date': forms.SelectDateWidget(),
        }

class HousekeepingForm(forms.ModelForm):
    room = forms.ModelChoiceField(queryset=Room.objects.all())
    status = forms.ChoiceField(choices=Room.STATUS_CHOICES)

    class Meta:
        model = Room
        fields = ['room', 'status']