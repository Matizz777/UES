from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.db import connection, IntegrityError
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from . import views
from datetime import datetime, timedelta

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', views.register_user, name='register'),
    path('api/login/', views.login_user, name='login'),
    path('api/my-reservations/', views.get_user_reservations),
    path('api/book/', views.save_booking, name='book'),
    path('api/occupied-times/', views.get_occupied_times, name='occupied_times'),
    path('api/cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('api/services/add/', views.add_service, name='add_service'),
    path('api/catalog/', views.get_providers, name='get_providers'),
    path('api/availability/', views.save_availability, name='availability'),
]