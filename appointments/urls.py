from django.urls import path
from . import views
import include

app_name = 'appointments'

urlpatterns = [
    path('calendar/', views.calendar_view, name='calendar'),
    path('lawyer_dashboard/', views.lawyer_dashboard, name='lawyer_dashboard'),
    path('create/<int:slot_id>/', views.create_appointment, name='create_appointment'),
    path('slots/', views.get_slots_api, name='get_slots_api'),
    path('update-status/<int:appointment_id>/', views.update_appointment_status, name='update_status'),
    path('select_slot/', views.select_slot, name='select_slot'),
    path('delete_slot/<int:slot_id>/', views.delete_slot, name='delete_slot'),
    path('create_slot_from_day/', views.create_slot_from_day, name='create_slot_from_day'),
    path('clear_rejected/', views.clear_rejected_appointments, name='clear_rejected'),
    path('clear-all-slots/', views.clear_all_slots, name='clear_all_slots'),
    path('generate-slots-days/', views.generate_slots_days, name='generate_slots_days'),
    path('appointment/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('cancel_appointment_client/<int:appointment_id>/', views.cancel_appointment_client, name='cancel_appointment_client'),
    path('appointment/cancel-by-client/<int:appointment_id>/', views.cancel_appointment_client, name='cancel_appointment_client'),
    path('download/general/<int:document_id>/', views.download_general_document, name='download_general_document'),
    path('download/appointment/<int:document_id>/', views.download_appointment_document, name='download_appointment_document'),
]
