from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_document = models.FileField(upload_to='id_documents/')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    is_blacklisted = models.BooleanField(default=False)

   

class Employees(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='employee_profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    



class Room(models.Model):
    ROOM_TYPES = (
        ('s', 'Single'),
        ('d', 'Double'),
        ('su', 'Suite'),
    )
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('cleaning', 'Needs Cleaning'),
        ('maintenance', 'Needs Maintenance'),
    ]
    name = models.CharField(max_length=255,  default='basic')  # New field for room name
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='available')
    room_type = models.CharField(max_length=2, choices=ROOM_TYPES)
    rate = models.DecimalField(max_digits=7, decimal_places=2,default=100.00)
    def is_available(self, start_date, end_date):
        bookings_for_room = Booking.objects.filter(room=self)
        for booking in bookings_for_room:
            if (start_date <= booking.end_date) and (end_date >= booking.start_date):
                return False  # Room is not available for these dates
        return True  # Room is available

class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/')


   
class ExtraCharge(models.Model):
    CHARGE_TYPES = (
        ('bed', 'Extra Bed'),
        ('smoking', 'Smoking Fee'),
        ('coffee','Coffe Price'),
        ('water','Water Price'),
        ('maintenance','Maintenance Price'),
        ('late','Late Fees'),
        ('early','Early Check Fee'),
        ('miscellaneous','Extra Fees')        
    )
    charge_type = models.CharField(max_length=50, choices=CHARGE_TYPES)
    cost = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.get_charge_type_display()
    

class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    accompanies = models.PositiveIntegerField(default=0, help_text="Number of people accompanying the customer.")
    charges = models.ManyToManyField(ExtraCharge, through='BookingCharge')


class BookingCharge(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    charge = models.ForeignKey(ExtraCharge, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    

class Payment(models.Model):
    STATUS = (
        ('p', 'Pending'),
        ('c', 'Completed'),
        ('f', 'Failed'),
        # Add more status types as needed
    )
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=1, choices=STATUS)

class Notification(models.Model):
    STATUS = (
        ('r', 'Read'),
        ('u', 'Unread'),
        # Add more status types as needed
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=1, choices=STATUS)



class Maintenance(models.Model):
    MAINTENANCE_STATUS = (
        ('r', 'Required'),
        ('p', 'Pending'),
        ('c', 'Completed'),
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    employees = models.ForeignKey(Employees, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=1, choices=MAINTENANCE_STATUS)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class StaffRegistrationRequest(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    employee_id = models.CharField(max_length=20)
    is_approved = models.BooleanField(default=False)



class AdminNotes(models.Model):
    note = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.note[:50]  # This returns the first 50 characters of the note for better representation.

