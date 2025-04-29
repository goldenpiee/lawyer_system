from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.core.serializers import serialize
from accounts.models import LawyerProfile
from .models import Appointment, CalendarSlot
from .forms import CalendarSlotForm
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.utils.timezone import make_aware, get_current_timezone
from django.core.mail import send_mail
from django.conf import settings
from zoneinfo import ZoneInfo
import json

@login_required
def client_profile(request):
    """
    Показывает профиль клиента с личной информацией и списком его заявок.
    """
    user = request.user
    appointments = user.client_appointments.all()
    return render(request, 'accounts/client_profile.html', {
        'user': user,
        'appointments': appointments,
    })

@login_required
def create_appointment(request, slot_id):
    try:
        slot = get_object_or_404(CalendarSlot, pk=slot_id)
        
        if slot.start_time < timezone.now():
            messages.error(request, "Нельзя записаться на прошедшее время")
            return redirect('appointments:calendar')
        
        # Проверяем существование отклоненной записи на это время
        existing_rejected = Appointment.objects.filter(
            lawyer=slot.lawyer,
            date=slot.start_time,
            status='Rejected'
        ).first()
        
        if existing_rejected:
            # Обновляем существующую отклоненную запись
            existing_rejected.status = 'Pending'
            existing_rejected.client = request.user
            existing_rejected.save()
            
            # Помечаем слот как занятый
            slot.is_booked = True
            slot.save()
            
            moscow_tz = ZoneInfo('Europe/Moscow')
            local_start_time = slot.start_time.astimezone(moscow_tz)
            messages.success(
                request,
                f"Запись успешно создана на {local_start_time.strftime('%d.%m.%Y %H:%M')} (МСК)"
            )
            return redirect('accounts:client_profile')
        
        # Если отклоненной записи нет, проверяем доступность слота
        if slot.is_booked:
            messages.error(request, "Этот слот уже занят")
            return redirect('appointments:calendar')
        
        # Создание новой записи
        Appointment.objects.create(
            client=request.user,
            lawyer=slot.lawyer,
            date=slot.start_time,
            status='Pending'
        )
        
        # Помечаем слот как занятый
        slot.is_booked = True
        slot.save()
        
        moscow_tz = ZoneInfo('Europe/Moscow')
        local_start_time = slot.start_time.astimezone(moscow_tz)
        messages.success(
            request,
            f"Запись успешно создана на {local_start_time.strftime('%d.%m.%Y %H:%M')} (МСК)"
        )
        return redirect('accounts:client_profile')
        
    except Exception as e:
        messages.error(request, f"Ошибка при создании записи: {str(e)}")
        return redirect('appointments:calendar')

def generate_slots(start_date, weeks=4):
    slots = []
    for week in range(weeks):
        for day in range(4):  # Вт-Пт (0=понедельник, 1=вторник...)
            current_date = start_date + timedelta(days=week*7 + day + 1)  # +1 чтобы начать со вторника
            if current_date.weekday() not in [1, 2, 3, 4]:  # 1=Вт, 4=Пт
                continue
            start_time = datetime.combine(current_date, datetime.strptime("14:00", "%H:%M").time())
            end_time = datetime.combine(current_date, datetime.strptime("18:00", "%H:%M").time())
            while start_time < end_time:
                slot_end = start_time + timedelta(minutes=30)
                slots.append((start_time, slot_end))
                start_time = slot_end
    return slots

@login_required
def select_slot(request):
    if not request.user.is_staff:
        messages.error(request, "Доступ запрещен. Вы не являетесь юристом.")
        return redirect('home')
    # Используем осведомленное время
    now = timezone.now()
    
    # Получаем доступные слоты для юриста (его пользователь)
    available_slots = CalendarSlot.objects.filter(
        lawyer=request.user,
        start_time__gte=now,  # Сравнение с осведомленной датой
        is_booked=False
    ).order_by('start_time')
    
    return render(request, 'appointments/select_slot.html', {'slots': available_slots})

@login_required(login_url='accounts:login')
def calendar_view(request):
    # Получаем текущую дату из параметра (для навигации по месяцам)
    current_date_str = request.GET.get('date')
    current_date = timezone.datetime.fromisoformat(current_date_str) if current_date_str else timezone.now()
    
    # Фильтруем слоты для выбранного месяца
    first_day = current_date.replace(day=1)
    last_day = (current_date + relativedelta(months=1)).replace(day=1) - timedelta(days=1)
    
    slots = CalendarSlot.objects.filter(
        start_time__gte=first_day,
        start_time__lte=last_day
    ).order_by('start_time')
    
    slots_json = serialize('json', slots, fields=('start_time', 'is_booked'))

    return render(request, 'appointments/calendar.html', {
        'slots_json': slots_json,
        'current_date': current_date.isoformat(),
    })

@login_required
@user_passes_test(lambda u: hasattr(u, 'lawyerprofile'))
def create_slot_from_day(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date_str = data.get('date')
            start_time_str = data.get('startTime')
            end_time_str = data.get('endTime')

            # Combine date and time strings
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()

            # Используем локальную временную зону (например, Europe/Moscow)
            tz = get_current_timezone()
            start_dt_local = datetime.combine(date_obj, start_time_obj)
            end_dt_local = datetime.combine(date_obj, end_time_obj)
            start_time = make_aware(start_dt_local, timezone=tz)
            end_time = make_aware(end_dt_local, timezone=tz)

            # Create the CalendarSlot
            CalendarSlot.objects.create(
                lawyer=request.user,
                start_time=start_time,
                end_time=end_time,
                is_booked=False
            )

            return HttpResponse("OK")
        except Exception as e:
            return HttpResponse(str(e), status=500)
    else:
        return HttpResponse("Invalid method", status=405)

@login_required
@user_passes_test(lambda u: hasattr(u, 'lawyerprofile'))
def delete_slot(request, slot_id):
    if request.method == 'POST':
        try:
            slot = CalendarSlot.objects.get(pk=slot_id)
            slot.delete()
            return HttpResponse("OK")
        except CalendarSlot.DoesNotExist:
            return HttpResponse("Slot not found", status=404)
        except Exception as e:
            return HttpResponse(str(e), status=500)
    else:
        return HttpResponse("Invalid method", status=405)

def get_slots_api(request):
    try:
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
        
        print(f"API: Requested slots for {year}-{month}")  # Отладочный вывод
        
        # Получаем начало и конец месяца с учетом временной зоны
        start_date = timezone.make_aware(datetime(year, month, 1))
        if month == 12:
            end_date = timezone.make_aware(datetime(year + 1, 1, 1))
        else:
            end_date = timezone.make_aware(datetime(year, month + 1, 1))
        
        # Получаем слоты для указанного месяца
        slots = CalendarSlot.objects.filter(
            start_time__gte=start_date,
            start_time__lt=end_date,
            is_booked=False  # Только свободные слоты
        ).order_by('start_time')
        
        print(f"API: Found {slots.count()} slots")  # Отладочный вывод
        
        # Сериализуем с добавлением временной зоны
        slots_json = serializers.serialize('json', slots)
        return JsonResponse({
            'slots': slots_json,
            'month': month,
            'year': year,
            'count': slots.count()
        })
    except Exception as e:
        print(f"API Error: {str(e)}")  # Отладочный вывод
        return JsonResponse({
            'error': str(e),
            'details': 'Ошибка при получении слотов'
        }, status=400)

@login_required
def lawyer_dashboard(request):
    print(f"User: {request.user.username}")  # Debugging
    print(f"Is staff: {request.user.is_staff}")  # Debugging
    print(f"Lawyer profile exists: {hasattr(request.user, 'lawyerprofile')}")  # Debugging
    
    if not request.user.is_staff:
        messages.error(request, "Доступ запрещен. Вы не являетесь юристом.")
        return redirect('home')
    
    status = request.GET.get('status', 'pending')
    status_map = {
        'pending': 'Pending',
        'approved': 'Approved',
        'rejected': 'Rejected'
    }
    
    appointments = Appointment.objects.select_related('client', 'client__lawyerprofile')
    pending_count = appointments.filter(status='Pending').count()
    approved_count = appointments.filter(status='Approved').count()
    rejected_count = appointments.filter(status='Rejected').count()
    
    current_status = status_map.get(status, 'pending')
    appointments = appointments.filter(status=current_status).order_by('-date')
    
    return render(request, 'appointments/lawyer_dashboard.html', {
        'appointments': appointments,
        'status': status,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count
    })

@login_required
def update_appointment_status(request, appointment_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
        
    appointment = get_object_or_404(Appointment, id=appointment_id)
    new_status = request.POST.get('status')
    
    if new_status in ['Approved', 'Rejected']:
        old_status = appointment.status
        appointment.status = new_status
        appointment.save()
        
        # Найти и обновить соответствующий слот
        try:
            slot = CalendarSlot.objects.get(
                lawyer=appointment.lawyer,
                start_time=appointment.date
            )
            if new_status == 'Rejected':
                # Если запись отменена, освобождаем слот
                slot.is_booked = False
                slot.save()
        except CalendarSlot.DoesNotExist:
            # Если слот не найден, создаем новый
            if new_status == 'Rejected':
                CalendarSlot.objects.create(
                    lawyer=appointment.lawyer,
                    start_time=appointment.date,
                    end_time=appointment.date + timedelta(minutes=30),
                    is_booked=False
                )
        
        # --- Отправка письма при подтверждении заявки ---
        if old_status != 'Approved' and new_status == 'Approved':
            moscow_tz = ZoneInfo('Europe/Moscow')
            local_dt = appointment.date.astimezone(moscow_tz)
            send_mail(
                'Ваша заявка подтверждена',
                f'Здравствуйте, {appointment.client.full_name}!\n\nВаша заявка на консультацию подтверждена. Ждём вас {local_dt.strftime("%d.%m.%Y в %H:%M")} (МСК).',
                'Юридические услуги по банкротству <matrica646@gmail.com>',
                [appointment.client.email],
                fail_silently=False,
            )
        # --- Отправка письма при отклонении заявки (если была Pending) ---
        if old_status == 'Pending' and new_status == 'Rejected':
            moscow_tz = ZoneInfo('Europe/Moscow')
            local_dt = appointment.date.astimezone(moscow_tz)
            send_mail(
                'Ваша заявка отклонена',
                f'Здравствуйте, {appointment.client.full_name}!\n\nК сожалению, ваша заявка на консультацию {local_dt.strftime("%d.%m.%Y в %H:%M")} (МСК) была отклонена. Вы можете выбрать другое время.',
                'Юридические услуги по банкротству <matrica646@gmail.com>',
                [appointment.client.email],
                fail_silently=False,
            )
        # --- Отправка письма при отмене подтвержденной заявки ---
        if old_status == 'Approved' and new_status == 'Rejected':
            moscow_tz = ZoneInfo('Europe/Moscow')
            local_dt = appointment.date.astimezone(moscow_tz)
            send_mail(
                'Ваша запись отменена',
                f'Здравствуйте, {appointment.client.full_name}!\n\nВаша ранее подтвержденная запись на {local_dt.strftime("%d.%m.%Y в %H:%M")} (МСК) была отменена юристом. Вы можете выбрать другое время.',
                'Юридические услуги по банкротству <matrica646@gmail.com>',
                [appointment.client.email],
                fail_silently=False,
            )

        if old_status == 'Approved' and new_status == 'Rejected':
            message = 'Запись успешно отменена'
        else:
            message = f'Статус записи успешно обновлен на {new_status}'
            
        messages.success(request, message)
    
    return redirect('appointments:lawyer_dashboard')

@login_required
def clear_rejected_appointments(request):
    if not request.user.is_staff:
        messages.error(request, "Доступ запрещен")
        return redirect('home')
        
    if request.method == 'POST':
        # Delete all rejected appointments
        deleted_count = Appointment.objects.filter(
            lawyer=request.user,
            status='Rejected'
        ).delete()[0]
        
        messages.success(
            request, 
            f"Успешно удалено {deleted_count} отклонённых записей"
        )
    
    return redirect('appointments:lawyer_dashboard')