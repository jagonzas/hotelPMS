from django.shortcuts import render, redirect
from .forms import StaffRegisterForm,CustomerRegisterForm, RoomForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Room, Booking, Payment, Customer, Staff, Blacklist, StaffRegistrationRequest
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

def managerooms(request):
    return render(request,'hotel_pms/login.html')




#Add room functionality only for admin 

@user_passes_test(lambda u: u.is_superuser, login_url='login')
def add_room(request):
    print(request.user.is_authenticated)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room added successfully.')
            return redirect('home')
    else:
        form = RoomForm()
    return render(request, 'hotel_pms/add_room.html', {'form': form})





