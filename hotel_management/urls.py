"""
URL configuration for hotel_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from hotel_pms import views
from django.urls import include
from django.conf import settings
from django.contrib.auth import views as auth_views
from hotel_pms.views import register_guest,register_select,register_staff, login_view


#put admin urls before admin.site.urls

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/hotel_rooms/', views.admin_rooms_view, name='admin_rooms'),
    path('admin/rooms/<int:room_id>/booking/', views.admin_book_room, name='admin_book_room'),
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', login_view, name='login'),
    path('save_notes/', views.save_notes, name='save_notes'),
    path('approve_registration', views.approve_registration, name='approve_registration'),
    path('list_bookings/', views.list_bookings, name='list_bookings'),
    path('edit_booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('view_guests/', views.view_guests, name='view_guests'),
    path('guest_detail/<int:guest_id>/', views.guest_detail, name='guest_detail'),
    path('manage/',views.managerooms, name='manage'),
    path('add_room/', views.add_room, name='add_room'),
    path('mybookings/', views.view_bookings, name='view_bookings'),
    path('mybookings/<int:booking_id>/', views.booking_details, name='booking_details'),
    path('mybookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('payment/<int:room_id>/<start_date>/<end_date>/', views.payment_page, name='payment_page'),
    path('make_payment/', views.make_payment, name='make_payment'),
    path('blacklist/', views.blacklist_customers, name='blacklist_customers'),
    path('room/<int:room_id>/book/', views.book_room, name='book_room'),
    path('manage_housekeeping/', views.manage_housekeeping, name='manage_housekeeping'),
    path('room/<int:pk>/', views.room_detail, name='room_detail'),
    path('delete-room/<int:pk>/', views.delete_room, name='delete_room'),
    path('manage/edit/<int:room_id>/', views.edit_room, name='edit_room'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/select/', views.register_select, name='register_select'),
    path('download_receipt/', views.download_receipt, name='download_receipt'),
    path('register/guest/', views.register_guest, name='register_guest'),
    path('register/staff/', views.register_staff, name='register_staff')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

