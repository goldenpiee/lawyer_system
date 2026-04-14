from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import LawyerProfile
from django.core.exceptions import ValidationError
from django.core import mail

class UserManagementTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_lawyer_profile_creation_and_uniqueness(self):
        lawyer = self.User.objects.create_user(
            email='lawyer@test.com',
            full_name='Lawyer',
            phone='+79991234569',
            password='pass'
        )
        LawyerProfile.objects.create(user=lawyer, specialization='BANKRUPTCY')
        
        with self.assertRaises(ValidationError):
            duplicate_profile = LawyerProfile(user=lawyer, specialization='FAMILY')
            duplicate_profile.full_clean()

class NotificationSystemTest(TestCase):
    def test_email_sending_flow(self):
        mail.send_mail(
            'Subject',
            'Body',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Subject')