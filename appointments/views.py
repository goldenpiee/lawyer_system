from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.core.serializers import serialize
from .models import Appointment, CalendarSlot
from django.http import JsonResponse, HttpResponse, Http404
from django.core import serializers
from django.utils.timezone import make_aware, get_current_timezone
from zoneinfo import ZoneInfo
from .forms import AppointmentDocumentForm
from .models import AppointmentDocument
from accounts.models import ClientDocument, CustomUser
from appointments.utils import send_email_notification
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

def is_lawyer(user):
    return user.is_authenticated and hasattr(user, 'lawyerprofile')

lawyer_required = user_passes_test(is_lawyer, login_url='accounts:login')

@login_required
def create_appointment(request, slot_id):
    with transaction.atomic(): 
        slot = get_object_or_404(CalendarSlot, pk=slot_id)
        
        if slot.start_time < timezone.now() or slot.is_booked:
            messages.error(request, "Слот недоступен")
            return redirect('appointments:calendar')

        existing_rejected = Appointment.objects.filter(
            lawyer=slot.lawyer, date=slot.start_time, status='Rejected'
        ).first()
        
        if existing_rejected:
            existing_rejected.status = 'Pending'
            existing_rejected.client = request.user
            existing_rejected.save()
        else:
            Appointment.objects.create(
                client=request.user,
                lawyer=slot.lawyer,
                date=slot.start_time,
                status='Pending'
            )

        slot.is_booked = True
        slot.save()
        
        local_dt = slot.start_time.astimezone(ZoneInfo('Europe/Moscow'))
        messages.success(request, f"Запись создана на {local_dt.strftime('%d.%m.%Y %H:%M')}")
        return redirect('accounts:client_profile')

@login_required
@lawyer_required
def select_slot(request):
    slots = CalendarSlot.objects.filter(lawyer=request.user, start_time__gte=timezone.now(), is_booked=False).order_by('start_time')
    return render(request, 'appointments/select_slot.html', {'slots': slots})

@login_required
def calendar_view(request):
    current_date = timezone.datetime.fromisoformat(request.GET.get('date')) if request.GET.get('date') else timezone.now()
    first_day = current_date.replace(day=1)
    last_day = (current_date + relativedelta(months=1)).replace(day=1) - timedelta(days=1)
    
    slots = CalendarSlot.objects.filter(start_time__gte=first_day, start_time__lte=last_day).order_by('start_time')
    return render(request, 'appointments/calendar.html', {
        'slots_json': serialize('json', slots, fields=('start_time', 'is_booked')),
        'current_date': current_date.isoformat(),
    })

@login_required
@lawyer_required
def create_slot_from_day(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        dt = datetime.combine(
            datetime.strptime(data.get('date'), '%Y-%m-%d').date(),
            datetime.strptime(data.get('startTime'), '%H:%M').time()
        )
        start_time = make_aware(dt, timezone=get_current_timezone())
        CalendarSlot.objects.create(lawyer=request.user, start_time=start_time, end_time=start_time + timedelta(minutes=30))
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
@lawyer_required
def delete_slot(request, slot_id):
    if request.method == 'POST':
        CalendarSlot.objects.filter(pk=slot_id).delete()
        return HttpResponse("OK")
    return HttpResponse("Invalid method", status=405)

@login_required
@lawyer_required
def clear_all_slots(request):
    if request.method == 'POST':
        CalendarSlot.objects.all().delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

def get_slots_api(request):
    year, month = int(request.GET.get('year')), int(request.GET.get('month'))
    start_date = timezone.make_aware(datetime(year, month, 1))
    end_date = timezone.make_aware(datetime(year + 1, 1, 1)) if month == 12 else timezone.make_aware(datetime(year, month + 1, 1))
    
    slots = CalendarSlot.objects.filter(start_time__gte=start_date, start_time__lt=end_date, is_booked=False).order_by('start_time')
    return JsonResponse({'slots': serializers.serialize('json', slots), 'month': month, 'year': year, 'count': slots.count()})

@login_required
@lawyer_required
def lawyer_dashboard(request):
    status_key = request.GET.get('status', 'pending')
    status_map = {'pending': 'Pending', 'approved': 'Approved', 'rejected': 'Rejected'}
    rus_map = {'pending': 'Ожидающие', 'approved': 'Подтвержденные', 'rejected': 'Отклоненные'}
    
    base_qs = Appointment.objects.select_related('client').filter(lawyer=request.user)
    
    return render(request, 'appointments/lawyer_dashboard.html', {
        'appointments': base_qs.filter(status=status_map.get(status_key, 'Pending')).order_by('-date'),
        'current_view_status_key': status_key, 
        'current_view_status_russian': rus_map.get(status_key),
        'pending_count': base_qs.filter(status='Pending').count(),
        'approved_count': base_qs.filter(status='Approved').count(),
        'rejected_count': base_qs.filter(status='Rejected').count(),
    })

@login_required
@lawyer_required
def lawyer_clients_list_view(request):
    client_ids = Appointment.objects.filter(lawyer=request.user).values_list('client_id', flat=True).distinct()
    return render(request, 'appointments/lawyer_clients_list.html', {
        'clients': CustomUser.objects.filter(id__in=client_ids).order_by('full_name'),
        'page_title': "Список ваших клиентов" 
    })

@login_required
@lawyer_required
def update_appointment_status(request, appointment_id):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=appointment_id)
        new_status = request.POST.get('status')
        
        if new_status in ['Approved', 'Rejected']:
            with transaction.atomic():   # <-- транзакция
                appointment.status = new_status
                appointment.save()
                
                slot, created = CalendarSlot.objects.get_or_create(
                    lawyer=appointment.lawyer,
                    start_time=appointment.date,
                    defaults={'end_time': appointment.date + timedelta(minutes=30)}
                )
                
                if new_status == 'Rejected':
                    slot.is_booked = False
                    slot.save()
                    subject, body = 'Заявка отклонена', f'Запись на {appointment.date.strftime("%d.%m.%Y")} отклонена.'
                else:
                    subject, body = 'Заявка подтверждена', f'Ждем вас {appointment.date.strftime("%d.%m.%Y %H:%M")}.'
                    
                send_email_notification(subject, body, appointment.client.email)
                messages.success(request, 'Статус обновлен')
                
    return redirect('appointments:lawyer_dashboard')

@login_required
@lawyer_required
def clear_rejected_appointments(request):
    if request.method == 'POST':
        Appointment.objects.filter(lawyer=request.user, status='Rejected').delete()
        messages.success(request, "Очищено")
    return redirect('appointments:lawyer_dashboard')

@csrf_exempt
@login_required
@lawyer_required
def generate_slots_days(request):
    if request.method == 'POST':
        dates, start_t, end_t = request.POST.get('selected_dates', ''), request.POST.get('start_time'), request.POST.get('end_time')
        if dates and start_t and end_t:
            count = 0
            for date_str in dates.split(','):
                try:
                    d_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    current = timezone.make_aware(datetime.combine(d_obj, datetime.strptime(start_t, "%H:%M").time()))
                    end_dt = timezone.make_aware(datetime.combine(d_obj, datetime.strptime(end_t, "%H:%M").time()))
                    
                    while current < end_dt:
                        if not CalendarSlot.objects.filter(lawyer=request.user, start_time=current).exists():
                            CalendarSlot.objects.create(lawyer=request.user, start_time=current, end_time=current + timedelta(minutes=30))
                            count += 1
                        current += timedelta(minutes=30)
                except ValueError:
                    pass
            return render(request, 'appointments/generate_slots_days.html', {'success': True, 'slots_created': count})
    return render(request, 'appointments/generate_slots_days.html')

@login_required
def cancel_appointment_client(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    
    if not appointment.can_cancel:
        messages.error(request, "Эту запись уже нельзя отменить.")
        return redirect('appointments:appointment_detail', appointment_id=appointment.id) 
        
    if request.method == 'POST':
        appointment.status = 'Rejected' 
        appointment.save()
        CalendarSlot.objects.filter(lawyer=appointment.lawyer, start_time=appointment.date).update(is_booked=False)
        
        send_email_notification(
            f"Отмена: {appointment.client.full_name}",
            f"Клиент отменил запись на {appointment.date.astimezone(ZoneInfo('Europe/Moscow')).strftime('%d.%m.%Y %H:%M')}.",
            appointment.lawyer.email
        )
        messages.success(request, "Запись отменена.")
        return redirect('accounts:client_profile')
        
    return render(request, 'appointments/confirm_cancel_client.html', {'appointment': appointment})

@login_required
def download_general_document(request, document_id):
    doc = get_object_or_404(ClientDocument, id=document_id, client=request.user)
    response = HttpResponse(doc.document.read(), content_type="application/octet-stream")
    response['Content-Disposition'] = f'inline; filename={doc.document.name.split("/")[-1]}'
    return response

@login_required
def download_appointment_document(request, document_id):
    doc = get_object_or_404(AppointmentDocument, id=document_id)
    if doc.appointment.client != request.user and doc.appointment.lawyer != request.user:
        raise Http404
        
    response = HttpResponse(doc.document.read(), content_type="application/octet-stream")
    response['Content-Disposition'] = f'inline; filename={doc.document.name.split("/")[-1]}'
    return response

@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    is_client = appointment.client == request.user
    is_lawyer_owner = appointment.lawyer == request.user
    
    if not (is_client or is_lawyer_owner):
        raise Http404

    if request.method == 'POST' and request.FILES:
        form = AppointmentDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.appointment = appointment
            doc.uploaded_by = request.user 
            doc.save()
            return redirect('appointments:appointment_detail', appointment_id=appointment.id) 

    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment,
        'documents': appointment.documents.all(),
        'upload_form': AppointmentDocumentForm(),
        'can_cancel': is_client and appointment.can_cancel,
        'is_client_owner': is_client, 
        'is_lawyer_for_appointment': is_lawyer_owner,
    })

@login_required
@lawyer_required
def lawyer_appointment_detail_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, lawyer=request.user)
    
    if request.method == 'POST': 
        form = AppointmentDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.appointment = appointment
            doc.uploaded_by = request.user
            doc.save()
            return redirect('appointments:lawyer_appointment_detail', appointment_id=appointment.id)

    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment,
        'documents': appointment.documents.all(),
        'upload_form': AppointmentDocumentForm(),
        'is_client_owner': False,
        'is_lawyer_for_appointment': True,
        'can_lawyer_approve': appointment.status == 'Pending', 
        'can_lawyer_cancel_approved': appointment.status == 'Approved'
    })

@login_required
@lawyer_required
def lawyer_client_profile_view(request, client_id):
    client = get_object_or_404(CustomUser, id=client_id)
    return render(request, 'appointments/lawyer_client_profile.html', {
        'client_user': client,
        'appointments': Appointment.objects.filter(client=client, lawyer=request.user).order_by('-date'),
        'general_documents': client.general_documents.all(),
    })