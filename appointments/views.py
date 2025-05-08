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
from django.core.mail import EmailMessage
from django.conf import settings
from zoneinfo import ZoneInfo
from .forms import AppointmentDocumentForm
from .models import AppointmentDocument
from accounts.forms import ClientDocumentForm
from accounts.models import ClientDocument
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404


@login_required
def client_profile(request):
    user = request.user
    
    # Логика для отображения записей (appointments)
    # Эта часть может быть упрощена, если can_cancel вычисляется в модели или шаблоне
    appointments_queryset = Appointment.objects.filter(client=user).select_related('lawyer').order_by('-date')
    appointments_with_cancel_info = []
    for appointment in appointments_queryset:
        can_cancel_deadline = appointment.date - timedelta(hours=24)
        appointment.can_cancel = (
            appointment.status in ['Pending', 'Approved'] and
            timezone.now() < can_cancel_deadline
        )
        # Также можно добавить загруженные документы к каждой записи, если нужно
        # appointment.attached_documents = appointment.documents.all() # Если related_name='documents'
        appointments_with_cancel_info.append(appointment)

    general_documents = user.general_documents.all()
    general_document_form = ClientDocumentForm() # Инициализация формы для GET

    if request.method == 'POST':
        # Проверяем, была ли нажата кнопка загрузки общего документа
        if 'upload_general_document' in request.POST:
            general_document_form = ClientDocumentForm(request.POST, request.FILES, instance=ClientDocument(client=user)) # instance можно так, или doc.client = user позже
            if general_document_form.is_valid():
                general_document_form.save() # Если instance был указан с client, то просто save()
                # Или:
                # doc = general_document_form.save(commit=False)
                # doc.client = user
                # doc.save()
                messages.success(request, 'Общий документ успешно загружен.')
                return redirect('accounts:client_profile')
            else:
                # Форма невалидна, ошибки будут в general_document_form.errors
                error_message_text = "Пожалуйста, исправьте ошибки: "
                for field, errors_list in general_document_form.errors.items():
                    error_message_text += f"{field}: {', '.join(errors_list)}. "
                messages.error(request, error_message_text.strip())
                # general_document_form с ошибками будет передан в контекст ниже
        # else:
            # Здесь может быть обработка других POST запросов, если они есть на этой странице
            # Например, если бы форма AppointmentDocumentForm отправлялась сюда же
            pass


    context = {
        'user': user,
        'appointments': appointments_with_cancel_info, # Передаем обработанный список
        'general_documents': general_documents,
        'general_document_form': general_document_form,
    }
    return render(request, 'accounts/client_profile.html', context)

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

            # Combine date and time strings
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()

            # Calculate end time (30 mins after start)
            end_time_obj = (datetime.combine(date_obj, start_time_obj) + timedelta(minutes=30)).time()

            # Используем локальную временную зону (например, Europe/Moscow)
            tz = get_current_timezone()
            start_dt_local = datetime.combine(date_obj, start_time_obj)
            end_dt_local = datetime.combine(date_obj, end_time_obj)
            start_time = make_aware(start_dt_local, timezone=tz)
            end_time = make_aware(end_dt_local, timezone=tz)

            # Create the CalendarSlot
            slot = CalendarSlot.objects.create(
                lawyer=request.user,
                start_time=start_time,
                end_time=end_time,
                is_booked=False
            )
            
            # Явно возвращаем сообщение
            return JsonResponse({
                'status': 'success',
                'message': f'Слот успешно создан на {start_time.strftime("%d.%m.%Y %H:%M")}'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': f'Ошибка при создании слота: {str(e)}'
            }, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

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

@login_required
@user_passes_test(lambda u: hasattr(u, 'lawyerprofile'))
def clear_all_slots(request):
    if request.method == 'POST':
        try:
            CalendarSlot.objects.all().delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

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
    if not request.user.is_staff:
        messages.error(request, "Доступ запрещен. Вы не являетесь юристом.")
        return redirect('home')
    
    status = request.GET.get('status', 'pending')
    status_map = {
        'pending': 'Pending',
        'approved': 'Approved',
        'rejected': 'Rejected'
    }
    
    # Filter appointments by current lawyer for all queries
    base_appointments = Appointment.objects.select_related('client', 'client__lawyerprofile').filter(lawyer=request.user)
    
    # Get counts for status badges
    pending_count = base_appointments.filter(status='Pending').count()
    approved_count = base_appointments.filter(status='Approved').count()
    rejected_count = base_appointments.filter(status='Rejected').count()
    
    current_status = status_map.get(status, 'pending')
    appointments = base_appointments.filter(status=current_status).order_by('-date')
    
    context = {
        'appointments': appointments,
        'status': status,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'appointments/lawyer_dashboard.html', context)

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
                slot.is_booked = False
                slot.save()
        except CalendarSlot.DoesNotExist:
            if new_status == 'Rejected':
                CalendarSlot.objects.create(
                    lawyer=appointment.lawyer,
                    start_time=appointment.date,
                    end_time=appointment.date + timedelta(minutes=30),
                    is_booked=False
                )
        
        # --- Отправка email уведомлений ---
        moscow_tz = ZoneInfo('Europe/Moscow')
        local_dt = appointment.date.astimezone(moscow_tz)
        email_data = None

        if old_status != 'Approved' and new_status == 'Approved':
            email_data = {
                'subject': 'Ваша заявка подтверждена',
                'body': f'Здравствуйте, {appointment.client.full_name}!\n\nВаша заявка на консультацию подтверждена. Ждём вас {local_dt.strftime("%d.%m.%Y")} в {local_dt.strftime("%H:%M")} (MSK).'
            }
            message = 'Заявка успешно подтверждена'
        elif old_status == 'Pending' and new_status == 'Rejected':
            email_data = {
                'subject': 'Ваша заявка отклонена',
                'body': f'Здравствуйте, {appointment.client.full_name}!\n\nК сожалению, ваша заявка на консультацию {local_dt.strftime("%d.%m.%Y")} в {local_dt.strftime("%H:%M")} (MSK) была отклонена. Вы можете выбрать другое время.'
            }
            message = 'Заявка успешно отклонена'
        elif old_status == 'Approved' and new_status == 'Rejected':
            email_data = {
                'subject': 'Ваша запись отменена',
                'body': f'Здравствуйте, {appointment.client.full_name}!\n\nВаша ранее подтвержденная запись на {local_dt.strftime("%d.%m.%Y")} в {local_dt.strftime("%H:%M")} (MSK) была отменена юристом. Вы можете выбрать другое время.'
            }
            message = 'Запись успешно отменена'

        if email_data:
            email = EmailMessage(
                subject=email_data['subject'],
                body=email_data['body'],
                from_email='Юридические услуги по банкротству <matrica646@gmail.com>',
                to=[appointment.client.email],
                headers={'Content-Type': 'text/plain; charset=utf-8'}
            )
            email.send(fail_silently=False)
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

@csrf_exempt
@login_required
@user_passes_test(lambda u: hasattr(u, 'lawyerprofile'))
def generate_slots_days(request):
    """
    Генерирует слоты на выбранные дни с указанным временем.
    """
    context = {}
    if request.method == 'POST':
        selected_dates = request.POST.get('selected_dates', '')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        if selected_dates and start_time and end_time:
            dates = selected_dates.split(',')
            slots_created = 0
            for date_str in dates:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    start_dt = timezone.make_aware(datetime.combine(date_obj, datetime.strptime(start_time, "%H:%M").time()))
                    end_dt = timezone.make_aware(datetime.combine(date_obj, datetime.strptime(end_time, "%H:%M").time()))
                    current = start_dt
                    while current < end_dt:
                        slot_end = current + timedelta(minutes=30)
                        # Avoid duplicates
                        from appointments.models import CalendarSlot
                        if not CalendarSlot.objects.filter(
                            lawyer=request.user,
                            start_time=current,
                            end_time=slot_end
                        ).exists():
                            CalendarSlot.objects.create(
                                lawyer=request.user,
                                start_time=current,
                                end_time=slot_end,
                                is_booked=False
                            )
                            slots_created += 1
                        current = slot_end
                except Exception as e:
                    continue
            context['success'] = True
            context['slots_created'] = slots_created
        else:
            context['error'] = "Не выбраны даты или не указано время."
    return render(request, 'appointments/generate_slots_days.html', context)
@login_required
def cancel_appointment_client(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    
    # Проверка, можно ли отменить запись (например, не менее чем за 24 часа)
    can_cancel_deadline = appointment.date - timedelta(hours=24) # Пример
    can_really_cancel = (
        appointment.status in ['Pending', 'Approved'] and
        timezone.now() < can_cancel_deadline
    )

    if not can_really_cancel:
        messages.error(request, "Эту запись уже нельзя отменить.")
        return redirect('appointments:appointment_detail', appointment_id=appointment.id) # Или в профиль

    if request.method == 'POST':
        # Логика отмены
        original_status = appointment.status
        appointment.status = 'Rejected' # Или 'CancelledByClient'
        appointment.save()

        # Освобождаем слот, если он был забронирован
        try:
            slot = CalendarSlot.objects.get(
                lawyer=appointment.lawyer,
                start_time=appointment.date,
                # is_booked=True # Можно добавить эту проверку
            )
            slot.is_booked = False
            slot.save()
        except CalendarSlot.DoesNotExist:
            # Слот мог быть удален или не создан, если запись импортирована
            # Либо создаем свободный слот (если это предусмотрено логикой)
            pass 
        except Exception as e:
            # Логируем ошибку освобождения слота, но продолжаем отмену записи
            print(f"Error unbooking slot for cancelled appointment {appointment.id}: {e}")


        # Уведомление юристу об отмене
        moscow_tz = ZoneInfo('Europe/Moscow') # Если не импортировано: from zoneinfo import ZoneInfo
        local_dt = appointment.date.astimezone(moscow_tz)
        
        email_subject = f"Клиент отменил запись на {local_dt.strftime('%d.%m.%Y %H:%M')}"
        email_body = (
            f"Уважаемый(-ая) {appointment.lawyer.full_name},\n\n"
            f"Клиент {appointment.client.full_name} ({appointment.client.email}) "
            f"отменил свою запись на {local_dt.strftime('%d.%m.%Y %H:%M')} (МСК).\n\n"
            f"Слот был автоматически освобожден в календаре (если существовал и был забронирован)."
        )
        try:
            email = EmailMessage(
                email_subject,
                email_body,
                from_email='Юридические услуги по банкротству <matrica646@gmail.com>', # Из settings.DEFAULT_FROM_EMAIL
                to=[appointment.lawyer.email]
            )
            email.send(fail_silently=False)
        except Exception as e:
            print(f"Error sending cancellation email to lawyer: {e}")
            messages.warning(request, "Запись отменена, но не удалось отправить уведомление юристу.")


        messages.success(request, "Запись успешно отменена.")
        return redirect('accounts:client_profile') # Редирект в профиль клиента
    
    # Для GET-запроса отображаем страницу подтверждения
    context = {
        'appointment': appointment
    }
    return render(request, 'appointments/confirm_cancel_client.html', context) # Новый шаблон
@login_required
def appointment_detail_client(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    documents = appointment.documents.all()
    upload_form = AppointmentDocumentForm()

    if request.method == 'POST':
        upload_form = AppointmentDocumentForm(request.POST, request.FILES)
        if upload_form.is_valid():
            doc = upload_form.save(commit=False)
            doc.appointment = appointment
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, f"Файл '{doc.document.name.split('/')[-1]}' успешно загружен.")
            return redirect('appointments:appointment_detail_client', appointment_id=appointment.id)
        else:
            messages.error(request, "Ошибка при загрузке файла.")

    context = {
        'appointment': appointment,
        'documents': documents,
        'upload_form': upload_form,
        # ... другие данные для client_profile ...
    }
    # Используйте существующий client_profile.html или создайте appointment_detail_client.html
    return render(request, 'accounts/client_profile.html', context)
@login_required
def download_general_document(request, document_id):
    from accounts.models import ClientDocument # Импорт здесь, чтобы избежать цикличности
    document = get_object_or_404(ClientDocument, id=document_id, client=request.user)
    # ... (логика скачивания как раньше) ...
    try:
        file_path = document.document.path
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'inline; filename={document.document.name.split("/")[-1]}'
            return response
    except FileNotFoundError:
        raise Http404

@login_required
def download_appointment_document(request, document_id):
    document = get_object_or_404(AppointmentDocument, id=document_id)
    # Проверка прав: клиент этой записи или юрист этой записи
    is_client_owner = document.appointment.client == request.user
    # Убедитесь, что request.user может иметь lawyerprofile
    is_lawyer_for_appointment = hasattr(request.user, 'lawyerprofile') and document.appointment.lawyer == request.user
    
    if not (is_client_owner or is_lawyer_for_appointment):
        raise Http404
    # ... (логика скачивания как раньше) ...
    try:
        file_path = document.document.path
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'inline; filename={document.document.name.split("/")[-1]}'
            return response
    except FileNotFoundError:
        raise Http404
@login_required
def appointment_detail(request, appointment_id): # Используем это имя, как в вашем urls.py и client_profile.html
    # Убеждаемся, что текущий пользователь - это клиент данной записи ИЛИ юрист данной записи
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Проверка прав доступа
    is_client_owner = appointment.client == request.user
    is_lawyer_for_appointment = hasattr(request.user, 'lawyerprofile') and appointment.lawyer == request.user
    
    if not (is_client_owner or is_lawyer_for_appointment):
        messages.error(request, "У вас нет прав для просмотра этой записи.")
        # Редирект на соответствующую страницу в зависимости от роли
        if hasattr(request.user, 'lawyerprofile'):
            return redirect('appointments:lawyer_dashboard')
        else:
            return redirect('accounts:client_profile')

    documents = appointment.documents.all() # related_name='documents' в модели AppointmentDocument
    upload_form = AppointmentDocumentForm()

    # Логика для возможности отмены клиентом
    can_cancel = False
    if is_client_owner:
        can_cancel_deadline = appointment.date - timedelta(hours=24) # Пример: за 24 часа
        can_cancel = (
            appointment.status in ['Pending', 'Approved'] and
            timezone.now() < can_cancel_deadline
        )

    if request.method == 'POST':
        # Обработка загрузки документа к этой записи
        # Убедитесь, что у кнопки submit в форме есть name, если форм на странице несколько
        # или если это единственная форма, то просто проверяем request.FILES
        if request.FILES: # Простая проверка, что файлы были отправлены
            upload_form = AppointmentDocumentForm(request.POST, request.FILES)
            if upload_form.is_valid():
                doc = upload_form.save(commit=False)
                doc.appointment = appointment
                doc.uploaded_by = request.user # Кто загрузил
                doc.save()
                messages.success(request, f"Документ '{doc.document.name.split('/')[-1]}' успешно прикреплен к записи.")
                return redirect('appointments:appointment_detail', appointment_id=appointment.id) # Редирект на эту же страницу
            else:
                messages.error(request, "Ошибка при загрузке документа к записи.")
    
    context = {
        'appointment': appointment,
        'documents': documents,
        'upload_form': upload_form,
        'can_cancel': can_cancel, # Передаем флаг для кнопки отмены
        'is_client_owner': is_client_owner, # Для условного отображения в шаблоне
        'is_lawyer_for_appointment': is_lawyer_for_appointment,
    }
    # Рендерим специализированный шаблон для деталей записи
    return render(request, 'appointments/appointment_detail.html', context)