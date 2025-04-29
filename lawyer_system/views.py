from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import Appointment

def confirm_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.confirmed = True
    appointment.save()
    # Отправка email пользователю
    send_mail(
        'Ваша заявка подтверждена',
        'Здравствуйте! Ваша заявка на консультацию подтверждена. Ждём вас в назначенное время.',
        'Юридические услуги по банкротству <matrica646@gmail.com>',
        [appointment.user.email],
        fail_silently=False,
    )