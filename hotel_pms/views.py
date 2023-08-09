from django.shortcuts import render, redirect
from .forms import StaffRegisterForm,CustomerRegisterForm, RoomForm , BookingForm, HousekeepingForm, EditBookingForm, BookingChargeFormSet, BookingCharge
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django import forms
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Room, Booking, Payment, Customer, Staff, StaffRegistrationRequest, RoomImage, BookingCharge
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

# Add other necessary imports here, such as your forms


# Create your views here.

def index(request):
    return render(request,'hotel_pms/index.html')

def home(request):
    rooms = Room.objects.all()
    print(request.user)  # Print the user
    print(request.user.groups.all())  # Print the user's groups

    is_guest = request.user.groups.filter(name='Customers').exists()
    print(is_guest)
    return render(request, 'hotel_pms/home.html', {'rooms': rooms, 'is_guest': is_guest})

def about(request):
    return render(request,'hotel_pms/about.html')



#REGISTERING

def register_select(request):
    return render(request,'hotel_pms/register_select.html')
    

def register_guest(request):
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # You've already created a Customer instance in your form's save method.
            # Customer.objects.create(user=user, id_document=request.FILES['id_document'])

            # Retrieve the group by name and add the user to it
            group = Group.objects.get(name='Customers')
            group.user_set.add(user)

            login(request, user)
            messages.success(request, f'Account created for {user.username}! You are now logged in.')
            return redirect('home')
        else:
            messages.error(request, 'There was an error in your registration. Please check your information.')
    else:
        form = CustomerRegisterForm()

    return render(request, 'hotel_pms/register_guest.html', {'form': form})


def register_staff(request):
    if request.method == 'POST':
        form = StaffRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            staff_id = form.cleaned_data.get('staff_id')
            StaffRegistrationRequest.objects.create(username=username, password=password, staff_id=staff_id)
            messages.success(request, f'Registration request for {username} has been submitted. You will receive an email once your account has been approved.')
            return redirect('login')
    else:
        form = StaffRegisterForm()
    return render(request, 'hotel_pms/register_staff.html', {'form': form})




#Request for admin to create staff acc (STAFF ACTION)

def approve_registration(request):
    if request.method == 'POST':
        staff_request_ids = request.POST.getlist('staff_request_id')
        for staff_request_id in staff_request_ids:
            staff_request = StaffRegistrationRequest.objects.get(id=staff_request_id)
            if staff_request and not staff_request.is_approved:
                # Create the staff user and add them to the staff group
                user = User.objects.create(username=staff_request.username, password=make_password(staff_request.password))
                group = Group.objects.get(name='Staff')
                user.groups.add(group)

                # Mark the request as approved
                staff_request.is_approved = True
                staff_request.save()

                messages.success(request, f'Account created for {staff_request.username}.')

    # Get all unapproved registration requests
    staff_requests = StaffRegistrationRequest.objects.filter(is_approved=False)
    return render(request, 'hotel_pms/approve_registration.html', {'staff_requests': staff_requests})



def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    return render(request, 'hotel_pms/room_detail.html', {'room': room})




def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"You are now logged in as {username}.")
            return redirect('home')
        else:
            messages.error(request,"Invalid username or password.")
            return render(request, 'hotel_pms/login.html') # added this line
    else:
        return render(request, 'hotel_pms/login.html')
    

#ROOMS

@user_passes_test(lambda u: u.is_superuser, login_url='login')
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    # For the formset without specifying a custom form
    BookingChargeFormSet = forms.inlineformset_factory(Booking, BookingCharge, fields=('charge', 'quantity'), extra=1)

    if request.method == 'POST':
        form = EditBookingForm(request.POST, instance=booking)
        formset = BookingChargeFormSet(request.POST, instance=booking)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('list_bookings')
        else:
            # If there's an error, you can optionally add a message or handle it as required
            messages.error(request, 'There was an error updating the booking. Please check the data and try again.')
    else:
        form = EditBookingForm(instance=booking)
        formset = BookingChargeFormSet(instance=booking)

    context = {
        'booking': booking,
        'form': form,
        'formset': formset
    }

    return render(request, 'hotel_pms/edit_booking.html', context)

@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            if room.is_available(start_date, end_date):
                # Create a new booking instance
                booking = form.save(commit=False) # don't save to DB yet
                booking.customer = request.user
                booking.room = room
                booking.save()
                return redirect('home')
            else:
                messages.error(request, 'Room is not available for the selected dates.')
        else:
            messages.error(request, 'There was an error with your booking. Please check the dates and try again.')

    else:
        form = BookingForm()  # This will create an empty form

    

    return render(request, 'hotel_pms/book_room.html', {'form': form, 'room': room})


def managerooms(request):
    # Check if the user is authenticated and is a staff member
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('home')
    
    # Retrieve all rooms
    rooms = Room.objects.all()
    return render(request, 'hotel_pms/manage_rooms.html', {'rooms': rooms})

@user_passes_test(lambda u: u.is_superuser, login_url='login')
def delete_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == "POST":
        room.delete()
        messages.success(request, "Room deleted successfully!")
        return redirect('manage')
    return render(request, 'hotel_pms/confirm_delete.html', {'room': room})


def edit_room(request, room_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('home')

    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)  # Note the addition of request.FILES to handle file uploads
        if form.is_valid():
            form.save()
            return redirect('manage')
    else:
        form = RoomForm(instance=room)
    
    return render(request, 'hotel_pms/edit_room.html', {'form': form})


def view_rooms(request):
    rooms = Room.objects.all().prefetch_related('roomimage_set')
    is_customer = request.user.groups.filter(name='Customers').exists()
    return render(request, 'hotel_pms/view_rooms.html', {'rooms': rooms})



#Add room functionality only for admin 

@login_required
def list_bookings(request):
    if not request.user.is_staff: # or `if not request.user.is_superuser:` if you want to restrict this only to superusers.
        return redirect('home') # or some other page

    # Order by start_date in ascending order
    bookings = Booking.objects.order_by('start_date')
    return render(request, 'hotel_pms/list_bookings.html', {'bookings': bookings})

@user_passes_test(lambda u: u.is_superuser, login_url='login')
def add_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            images = request.FILES.getlist('images')
            for img in images:
                RoomImage.objects.create(room=room, image=img)
            messages.success(request, 'Room added successfully.')
            return redirect('home')
    else:
        form = RoomForm()
    return render(request, 'hotel_pms/add_room.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser, login_url='login')
def manage_housekeeping(request):
    rooms = Room.objects.all()
    if request.method == 'POST':
        form = HousekeepingForm(request.POST)
        if form.is_valid():
            room = form.cleaned_data['room']
            status = form.cleaned_data['status']
            room.status = status
            room.save()
            messages.success(request, 'Room status updated successfully.')
    else:
        form = HousekeepingForm()
    return render(request, 'hotel_pms/manage_housekeeping.html', {'rooms': rooms, 'form': form})

