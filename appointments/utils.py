from django.core.mail import EmailMessage
from django.conf import settings

def send_email_notification(subject, body, to_email):
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
        headers={'Content-Type': 'text/plain; charset=utf-8'}
    )
    email.send(fail_silently=False)