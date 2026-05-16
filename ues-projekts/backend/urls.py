from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', views.register_user, name='register'),
    path('api/login/', views.login_user, name='login'),
    path('api/my-reservations/', views.get_user_reservations),
    path('api/book/', views.save_booking, name='book'),
    path('api/occupied-times/', views.get_occupied_times, name='occupied_times'),
    path('api/cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('api/reschedule-booking/<int:booking_id>/', views.reschedule_booking, name='reschedule_booking'),
    path('api/services/add/', views.add_service, name='add_service'),
    path('api/catalog/', views.get_providers, name='get_providers'),
    path('api/availability/', views.add_availability, name='availability'),
    path('api/services/my/', views.get_my_services, name='my-services'),
    path('api/services/edit/<int:service_id>/', views.edit_service, name='edit-service'),
    path('api/services/delete/<int:service_id>/', views.delete_service, name='delete-service'),
    path('api/provider-calendar/', views.get_provider_calendar, name='provider-calendar'),
    path('api/notifications/', views.get_notifications, name='notifications'),
    path('api/notifications/read/', views.mark_notifications_read, name='notifications-read'),
    path('api/notifications/delete/<int:notif_id>/', views.delete_notification, name='notification-delete'),
]