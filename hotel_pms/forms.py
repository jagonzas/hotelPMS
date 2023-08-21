from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Room, Customer, Booking, BookingCharge


class CustomerRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    id_document = forms.FileField(help_text='Required. Upload your ID document.')
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'id_document', 'profile_picture']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()

        customer_profile = Customer(user=user, id_document=self.cleaned_data['id_document'], profile_picture=self.cleaned_data['profile_picture'])
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
        fields = ['name','room_type','rate']
        widgets = {
            'room_type': forms.Select(choices=Room.ROOM_TYPES),
            'rate': forms.NumberInput(attrs={'step': "0.01", 'min': "0"}),
            'image': forms.FileInput()
        }


class BookingForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("End date should be after the start date.")


class HousekeepingForm(forms.ModelForm):
    room = forms.ModelChoiceField(queryset=Room.objects.all())
    status = forms.ChoiceField(choices=Room.STATUS_CHOICES)

    class Meta:
        model = Room
        fields = ['room', 'status']


class EditBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['accompanies']
        exclude = ['charges']
        

BookingChargeFormSet = forms.inlineformset_factory(
    Booking, 
    BookingCharge, 
    fields=('charge', 'quantity'), 
    extra=1, 
    can_delete=True
)
