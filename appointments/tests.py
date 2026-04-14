from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import LawyerProfile
from .models import CalendarSlot, Appointment

class AppointmentFlowTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client_user = User.objects.create_user(email='client@test.com', full_name='C', phone='+70000000001', password='pass')
        self.lawyer_user = User.objects.create_user(email='lawyer@test.com', full_name='L', phone='+70000000002', password='pass', is_staff=True)
        LawyerProfile.objects.create(user=self.lawyer_user, specialization='BANKRUPTCY')
        self.client = Client()

    def test_successful_booking(self):
        slot = CalendarSlot.objects.create(
            lawyer=self.lawyer_user,
            start_time=timezone.now() + timezone.timedelta(days=1),
            end_time=timezone.now() + timezone.timedelta(days=1, hours=1)
        )
        
        self.client.login(email='client@test.com', password='pass')
        self.client.post(reverse('appointments:create_appointment', args=[slot.id]))
        
        slot.refresh_from_db()
        self.assertTrue(slot.is_booked)
        self.assertEqual(Appointment.objects.filter(client=self.client_user, lawyer=self.lawyer_user).count(), 1)

    def test_lawyer_can_reject_appointment(self):
        appointment = Appointment.objects.create(
            client=self.client_user,
            lawyer=self.lawyer_user,
            date=timezone.now() + timezone.timedelta(days=1),
            status='Approved'
        )
        
        self.client.login(email='lawyer@test.com', password='pass')
        self.client.post(reverse('appointments:update_status', args=[appointment.id]), {'status': 'Rejected'})
        
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'Rejected')