from io import BytesIO
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import EmployeeRegisterForm,DateSelectionForm,CustomerRegisterForm, RoomForm , BookingForm, HousekeepingForm, EditBookingForm, BookingChargeFormSet, BookingCharge
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django import forms
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Room, Booking, Payment, Customer, Employees, StaffRegistrationRequest, AdminNotes ,RoomImage, BookingCharge
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from django.http import HttpResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from decimal import Decimal
import stripe
from xhtml2pdf import pisa
from django.template.loader import get_template

# Add other necessary imports here, such as your forms


#Payment keys
STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY


stripe.api_key = STRIPE_SECRET_KEY

# to check if admin or employee, to be used in future view functions
def superuser_or_employee_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not (request.user.is_superuser or hasattr(request.user, 'employee_profile')):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func



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

def cheking_employee(request):
    is_employee = request.user.groups.filter(name='Employees').exists()

    context = {
        'is_employee': is_employee,
        # ... any other context data you have ...
    }

    return render(request, 'che.html', context)



def calculate_days( start_date, end_date):
    return (end_date - start_date).days

def calculate_amount(room_rate, start_date, end_date):
    days = calculate_days(start_date, end_date)
    return room_rate * days * 100 #Amount in cents
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
        form = EmployeeRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            employee_id = form.cleaned_data.get('employee_id')
            StaffRegistrationRequest.objects.create(username=username, password=password, employee_id=employee_id)
            messages.success(request, f'Registration request for {username} has been submitted. You will receive an email once your account has been approved.')
            return redirect('login')
    else:
        form = EmployeeRegisterForm()
    return render(request, 'hotel_pms/register_staff.html', {'form': form})




#Request for admin to create employee acc (employee ACTION)
def approve_registration(request):
    if request.method == 'POST':
        # Handle Approvals:
        employee_request_ids = request.POST.getlist('employee_request_id')
        for employee_request_id in employee_request_ids:
            employee_request = StaffRegistrationRequest.objects.get(id=employee_request_id)
            if employee_request and not employee_request.is_approved:
                # Create the staff user and add them to the staff group
                user = User.objects.create(username=employee_request.username, password=make_password(employee_request.password))
                group = Group.objects.get(name='Employees')
                user.groups.add(group)

                # Mark the request as approved
                employee_request.is_approved = True
                employee_request.save()

                messages.success(request, f'Account created for {employee_request.username}.')

        # Handle Denials:
        deny_employee_request_ids = request.POST.getlist('deny_employee_request_id')
        for deny_employee_request_id in deny_employee_request_ids:
            deny_employee_request = StaffRegistrationRequest.objects.get(id=deny_employee_request_id)
            if deny_employee_request and not deny_employee_request.is_approved:
                deny_employee_request.delete()  # This deletes the request, but you can also choose to mark it as denied if you add such a field
                messages.success(request, f'Registration request for {deny_employee_request.username} has been denied and deleted.')

    # Get all unapproved registration requests
    employee_requests = StaffRegistrationRequest.objects.filter(is_approved=False)
    return render(request, 'hotel_pms/approve_registration.html', {'employee_requests': employee_requests})




def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    return render(request, 'hotel_pms/room_detail.html', {'room': room})




def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user has a customer attribute and if they are blacklisted
            if hasattr(user, 'customer') and user.customer.is_blacklisted:
                messages.error(request, "Your account has been blacklisted. Please contact the establishment.")
                return render(request, 'hotel_pms/login.html')
            login(request, user)
            messages.success(request, f"You are now logged in as {username}.")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'hotel_pms/login.html')
    else:
        return render(request, 'hotel_pms/login.html')

    

#ROOMS

@user_passes_test(lambda u: u.is_superuser, login_url='login')
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    if request.method == 'POST':
        if 'delete_entire_booking' in request.POST:
            booking.delete()
            return redirect('list_bookings') # Redirect to bookings list after deletion

        form = EditBookingForm(request.POST, instance=booking)
        formset = BookingChargeFormSet(request.POST, instance=booking)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('list_bookings')
        else:
            print ("Formset errors:", formset.errors) #debug line
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
            print ("form is valid")
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            if room.is_available(start_date, end_date):
                

                booking = form.save(commit=False)
                booking.customer = request.user
                booking.room = room
                booking.save()
                return redirect('payment_page', room_id=room.id, start_date=start_date, end_date=end_date)
                # return redirect('home')
            else:
                messages.error(request, 'Room is not available for the selected dates.')
        else:
            print ("form is invalid")
            messages.error(request, 'There was an error with your booking. Please check the dates and try again.')

    else:
        form = BookingForm()  # This will create an empty form

    

    return render(request, 'hotel_pms/book_room.html', {'form': form, 'room': room})




#Payments: 
def payment_page(request, room_id, start_date, end_date):
    room = get_object_or_404(Room, pk=room_id)
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    num_days = (end_date_obj - start_date_obj).days
    total_cost = room.rate * num_days

    context = {
        'room': room,
        'start_date': start_date_obj,
        'end_date': end_date_obj,
        'total_cost': total_cost,
        'stripe_public_key': STRIPE_PUBLIC_KEY
    }
    return render(request, 'hotel_pms/payment_page.html', context)


#Stripe and actual charge : 
@login_required
def make_payment(request):
    if request.method == "POST":
        
        token = request.POST['stripeToken']
        amount = int(float(request.POST.get('amount', 0)) * 100)
        
        
        if 'stripeToken' in request.POST:
            token = request.POST['stripeToken']
        else:
            messages.error(request, "Payment failed. Stripe token was not received.")
            return redirect('payment_page')


        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
                description=f"Payment for Room Booking by {request.user.username}"
            )
            # Save the charge ID or any other info in your DB if necessary
            messages.success(request, "Payment successful!")
            return redirect('home')
        except stripe.error.CardError as e:
            messages.error(request, "Your card was declined!")
    return redirect('payment_page')





@user_passes_test(lambda u: u.is_superuser, login_url='login')
def managerooms(request):
   
    
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

@user_passes_test(lambda u: u.is_superuser, login_url='login')
def edit_room(request, room_id):
   
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






def save_notes(request):
    if request.method == "POST":
        note_text = request.POST.get('notes')
        if note_text:
            AdminNotes.objects.create(note=note_text)
        return redirect('list_bookings')  # Redirect back to the booking list after saving.

@superuser_or_employee_required
def list_bookings(request):
    


    admin_notes = AdminNotes.objects.all().order_by('-timestamp')

    if 'delete_note' in request.POST and request.user.is_superuser:
        note_id = request.POST['delete_note']
        try:
            note = AdminNotes.objects.get(id=note_id)
            note.delete()
        except AdminNotes.DoesNotExist:
            # Optionally handle if the note doesn't exist; might not be necessary
            pass


    # Order by start_date in ascending order
    bookings = Booking.objects.order_by('start_date')
    context = {
        'admin_notes': admin_notes,
        'bookings': bookings
    }
    return render(request, 'hotel_pms/list_bookings.html', context)


#Add room functionality only for admin 
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


@superuser_or_employee_required
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







@user_passes_test(lambda u: u.is_superuser, login_url='login')
def admin_rooms_view(request):
    rooms = Room.objects.all()
    return render(request, 'hotel_pms/admin_rooms.html', {'rooms': rooms})

@superuser_or_employee_required
def admin_book_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            # Create a new booking instance
            booking = form.save(commit=False) # don't save to DB yet
            booking.customer = request.user
            booking.room = room
            booking.save()
            return redirect('list_bookings') # or wherever you want to redirect after the admin makes a booking
        else:
            messages.error(request, 'There was an error with your booking. Please check the form.')

    else:
        form = BookingForm()  # This will create an empty form

    return render(request, 'hotel_pms/admin_book_room.html', {'form': form, 'room': room})



@superuser_or_employee_required
def blacklist_customers(request):
    query = request.GET.get('q')
    customers = Customer.objects.all()
    
    if query:
        customers = customers.filter(user__username__icontains=query)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = Customer.objects.get(id=user_id)
        user.is_blacklisted = not user.is_blacklisted  # toggle the status
        user.save()
        return redirect('blacklist_customers')

    return render(request, 'hotel_pms/blacklist.html', {'customers': customers})

def view_guests(request):
    guests = Customer.objects.all()
    return render(request, 'hotel_pms/view_guests.html', {'guests': guests})


def guest_detail(request, guest_id):
    guest = Customer.objects.get(id=guest_id)
    return render(request, 'hotel_pms/guest_detail.html', {'guest': guest})



def guest_detail_pdf(request, guest_id):
    guest = Customer.objects.get(id=guest_id)
    template_path = 'hotel_pms/guest_detail_pdf.html'
    context = {'guest': guest,
               'request':request,
               }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="registration.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
       html.encode("ISO-8859-1"), dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


#customers view of their bookings 

@login_required
def view_bookings(request):
    # Retrieve all bookings for the logged-in user
    bookings = Booking.objects.filter(customer=request.user)
    return render(request, 'hotel_pms/view_bookings.html', {'bookings': bookings})

def calculate_total_cost(room, start_date, end_date):
    num_days = (end_date - start_date).days
    return room.rate * num_days


@login_required
def booking_details(request, booking_id):
    # Retrieve the specific booking details
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    total_cost = calculate_total_cost(booking.room, booking.start_date, booking.end_date)
    
    return render(request, 'hotel_pms/booking_details.html', {'booking': booking, 'total_cost': total_cost})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, "Booking cancelled successfully!")
        return redirect('view_bookings')
    return render(request, 'hotel_pms/confirm_cancel.html', {'booking': booking})




def booking_receipt(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    total_cost = calculate_total_cost(booking.room, booking.start_date, booking.end_date)
    return render(request, 'hotel_pms/booking_receipt.html', {'booking': booking, 'total_cost': total_cost})


@user_passes_test(lambda u: u.is_superuser, login_url='login')
def generate_receipt_pdf(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Calculate additional fields
    booking.nights = (booking.end_date - booking.start_date).days
    booking.rate = booking.room.rate  # Ensure room rate is accessible like this

    # Fetch and calculate total extra charges
    booking_charges = BookingCharge.objects.filter(booking=booking)
    total_extra_charges = sum([bc.charge.cost * bc.quantity for bc in booking_charges])
    
    booking.total_cost = (booking.nights * booking.rate) + total_extra_charges  # Calculate the total cost including extra charges

    # Load the template
    template = get_template('hotel_pms/booking_receipt.html')  # Replace with your actual path

    # Render the template with the booking context
    html = template.render({'booking': booking, 'booking_charges': booking_charges, 'total_extra_charges': total_extra_charges})
    
    # Generate the PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Check for errors
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response


#tester
def test_guest_detail_html(request, guest_id):
    guest = Customer.objects.get(id=guest_id)
    context = {'guest': guest}
    return render(request, 'hotel_pms/guest_detail_pdf.html', context)



def select_date_view(request):
    form = DateSelectionForm()
    return render(request, 'hotel_pms/select_date.html', {'form': form})



def fetch_data(request):
    if request.method == 'POST':
        form = DateSelectionForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            bookings = Booking.objects.filter(start_date__gte=start_date, end_date__lte=end_date)
            
            for booking in bookings:
                nights = (booking.end_date - booking.start_date).days
                total_price = booking.room.rate * nights

                extra_charges = BookingCharge.objects.filter(booking=booking)
                extra_charges_details = []
                extra_charges_total_price = 0

                for charge in extra_charges:
                    total_price += charge.charge.cost * charge.quantity
                    extra_charges_details.append({
                        'description': charge.charge.charge_type,
                        'quantity': charge.quantity,
                        'total_cost': charge.charge.cost * charge.quantity
                    })
                    extra_charges_total_price += charge.charge.cost * charge.quantity
                
                price_before_tax = total_price / Decimal('1.08')
                tax_amount = total_price - price_before_tax

                booking.nights = nights
                booking.total_price = total_price
                booking.price_before_tax = price_before_tax
                booking.tax_amount = tax_amount
                booking.extra_charges_details = extra_charges_details
                booking.extra_charges_total_price = extra_charges_total_price

            template = get_template('hotel_pms/receipt_template.html')
            html_content = template.render({'bookings': bookings})
            
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="report.pdf"'
            pisa_status = pisa.CreatePDF(html_content, dest=response)
            if pisa_status.err:
                return HttpResponse('Error generating PDF', status=500)
            return response
    else:
        form = DateSelectionForm()
    return render(request, 'hotel_pms/select_date.html', {'form': form})



