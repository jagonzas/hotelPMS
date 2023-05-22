from django.contrib.auth.models import User
from django.db import models


class Inventory(models.Model):
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()

    
class Service(models.Model):
    service_name = models.CharField(max_length=100)


class UserProfile(models.Model):
    USER_CLASSES = [
        ('customer','Customer'),
        ('staff','Staff'),
        ('management','Management'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_class = models.CharField(max_length=20, choices=USER_CLASSES)
    services = models.ManyToManyField(Service)
    inventory = models.ManyToManyField(Inventory)



class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
        ('penthouse','Penthouse'),
    ]
    room_number = models.IntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    availability = models.BooleanField(default=True)

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()


class Employee(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    services = models.ManyToManyField(Service)
