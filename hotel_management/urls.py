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

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', login_view, name='login'),
    path('approve_registration', views.approve_registration, name='approve_registration'),
    path('manage/',views.managerooms, name='manage'),
    path('add_room/', views.add_room, name='add_room'),
    path('view_rooms/', views.view_rooms, name='view_rooms'),
    path('manage_housekeeping/', views.manage_housekeeping, name='manage_housekeeping'),
    path('room/<int:pk>/', views.room_detail, name='room_detail'),
    path('manage/edit/<int:room_id>/', views.edit_room, name='edit_room'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/select/', views.register_select, name='register_select'),
    path('register/guest/', views.register_guest, name='register_guest'),
    path('register/staff/', views.register_staff, name='register_staff')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
