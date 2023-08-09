from django.contrib import admin
from .models import Room, RoomImage, Booking, ExtraCharge, BookingCharge



class BookingChargeInline(admin.TabularInline):  # TabularInline will display it in a table format
    model = BookingCharge
    extra = 1  # Number of empty forms to display

class BookingAdmin(admin.ModelAdmin):
    inlines = [BookingChargeInline]


    
class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

class RoomAdmin(admin.ModelAdmin):
    inlines = [RoomImageInline]

    

admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(ExtraCharge)