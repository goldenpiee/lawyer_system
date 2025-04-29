from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Appointment

def confirm_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.confirmed = True
    appointment.save()
    # Отправка email пользователю
    email = EmailMessage(
        subject='Ваша заявка подтверждена',
        body='Здравствуйте! Ваша заявка на консультацию подтверждена. Ждём вас в назначенное время.',
        from_email='Юридические услуги по банкротству <matrica646@gmail.com>',
        to=[appointment.user.email],
        headers={'Content-Type': 'text/plain; charset=utf-8'}
    )
    email.send(fail_silently=False)