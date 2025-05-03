from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import LawyerProfile
from .models import CalendarSlot, Appointment

class AppointmentsBasicTest(TestCase):
    def test_dummy(self):
        print("\n[ТЕСТ] AppointmentsBasicTest: Простой тест-заглушка (проверка работы тестовой среды)")
        try:
            self.assertTrue(True)
            print("  └─ ✅ Тест-заглушка успешно выполнен")
        except Exception as e:
            print("  └─ ❌ Ошибка:", e)
            raise

class AppointmentsAdvancedTest(TestCase):
    def setUp(self):
        print("\n[НАСТРОЙКА] AppointmentsAdvancedTest: создание тестовых пользователей и профиля юриста")
        self.User = get_user_model()
        self.client_user = self.User.objects.create_user(
            email='client@test.com',
            full_name='Client User',
            phone='+79991234568',
            password='pass123'
        )
        self.lawyer_user = self.User.objects.create_user(
            email='lawyer@test.com',
            full_name='Lawyer User',
            phone='+79991234569',
            password='pass123',
            is_staff=True
        )
        self.lawyer_profile = LawyerProfile.objects.create(user=self.lawyer_user, specialization='BANKRUPTCY')
        self.client = Client()
        print("  └─ Пользователь-клиент:", self.client_user.email)
        print("  └─ Пользователь-юрист:", self.lawyer_user.email)

    def test_create_calendar_slot(self):
        print("\n[ТЕСТ] AppointmentsAdvancedTest: Проверка создания слота в календаре (CalendarSlot)")
        try:
            slot = CalendarSlot.objects.create(
                lawyer=self.lawyer_user,
                start_time=timezone.now() + timezone.timedelta(days=1, hours=2),
                end_time=timezone.now() + timezone.timedelta(days=1, hours=3),
                is_booked=False
            )
            print("  └─ Создан слот:", slot)
            self.assertEqual(slot.lawyer, self.lawyer_user)
            self.assertFalse(slot.is_booked)
            print("  └─ ✅ Тест пройден: слот создан и не занят")
        except Exception as e:
            print("  └─ ❌ Ошибка:", e)
            raise

    def test_book_slot_and_create_appointment(self):
        print("\n[ТЕСТ] AppointmentsAdvancedTest: Проверка бронирования слота и создания записи (Appointment)")
        try:
            slot = CalendarSlot.objects.create(
                lawyer=self.lawyer_user,
                start_time=timezone.now() + timezone.timedelta(days=1, hours=2),
                end_time=timezone.now() + timezone.timedelta(days=1, hours=3),
                is_booked=False
            )
            self.client.login(email='client@test.com', password='pass123')
            response = self.client.post(reverse('appointments:create_appointment', args=[slot.id]))
            print("  └─ Ответ на бронирование слота:", response.status_code)
            slot.refresh_from_db()
            self.assertTrue(slot.is_booked)
            self.assertEqual(Appointment.objects.count(), 1)
            appointment = Appointment.objects.first()
            print("  └─ Создана запись:", appointment)
            self.assertEqual(appointment.client, self.client_user)
            self.assertEqual(appointment.lawyer, self.lawyer_user)
            print("  └─ ✅ Тест пройден: слот забронирован и запись создана")
        except Exception as e:
            print("  └─ ❌ Ошибка:", e)
            raise

    def test_cancel_appointment(self):
        print("\n[ТЕСТ] AppointmentsAdvancedTest: Проверка отмены записи (Appointment.status -> Rejected)")
        try:
            slot = CalendarSlot.objects.create(
                lawyer=self.lawyer_user,
                start_time=timezone.now() + timezone.timedelta(days=1, hours=2),
                end_time=timezone.now() + timezone.timedelta(days=1, hours=3),
                is_booked=True
            )
            appointment = Appointment.objects.create(
                client=self.client_user,
                lawyer=self.lawyer_user,
                date=slot.start_time,
                status='Approved'
            )
            self.client.login(email='lawyer@test.com', password='pass123')
            response = self.client.post(reverse('appointments:update_status', args=[appointment.id]), {'status': 'Rejected'})
            print("  └─ Ответ на отмену записи:", response.status_code)
            appointment.refresh_from_db()
            print("  └─ Статус записи после отмены:", appointment.status)
            self.assertEqual(appointment.status, 'Rejected')
            print("  └─ ✅ Тест пройден: статус записи изменён на 'Rejected'")
        except Exception as e:
            print("  └─ ❌ Ошибка:", e)
            raise

    def test_calendar_view_access(self):
        print("\n[ТЕСТ] AppointmentsAdvancedTest: Проверка доступа к календарю для клиента и неавторизованного пользователя")
        try:
            self.client.login(email='client@test.com', password='pass123')
            response = self.client.get(reverse('appointments:calendar'))
            print("  └─ Код ответа для авторизованного клиента:", response.status_code)
            self.assertEqual(response.status_code, 200)
            self.client.logout()
            response = self.client.get(reverse('appointments:calendar'))
            print("  └─ Код ответа для неавторизованного пользователя:", response.status_code)
            self.assertEqual(response.status_code, 302)
            print("  └─ ✅ Тест пройден: доступ к календарю корректен для разных пользователей")
        except Exception as e:
            print("  └─ ❌ Ошибка:", e)
            raise

    def test_lawyer_dashboard_access(self):
        print("\n[ТЕСТ] AppointmentsAdvancedTest: Проверка доступа к панели юриста (lawyer_dashboard)")
        try:
            self.client.login(email='lawyer@test.com', password='pass123')
            response = self.client.get(reverse('appointments:lawyer_dashboard'))
            print("  └─ Код ответа для юриста:", response.status_code)
            self.assertEqual(response.status_code, 200)
            self.client.logout()
            self.client.login(email='client@test.com', password='pass123')
            response = self.client.get(reverse('appointments:lawyer_dashboard'))
            print("  └─ Код ответа для клиента (ожидается редирект):", response.status_code)
            self.assertEqual(response.status_code, 302)
            print("  └─ ✅ Тест пройден: панель юриста доступна только юристу")
        except Exception as e:
            print("  └─ ❌ Ошибка:", e)
            raise

    def test_lawyer_sees_only_own_appointments(self):
        print("\n[ТЕСТ] AppointmentsAdvancedTest: Проверка видимости подтвержденных записей только для назначенного юриста")
        try:
            # Create another lawyer
            another_lawyer = get_user_model().objects.create_user(
                email='another_lawyer@test.com',
                full_name='Another Lawyer',
                phone='+79991234567',
                password='pass123',
                is_staff=True
            )
            LawyerProfile.objects.create(user=another_lawyer, specialization='BANKRUPTCY')
            
            # Create appointments for both lawyers
            slot1 = CalendarSlot.objects.create(
                lawyer=self.lawyer_user,
                start_time=timezone.now() + timezone.timedelta(days=1),
                end_time=timezone.now() + timezone.timedelta(days=1, hours=1),
                is_booked=True
            )
            slot2 = CalendarSlot.objects.create(
                lawyer=another_lawyer,
                start_time=timezone.now() + timezone.timedelta(days=2),
                end_time=timezone.now() + timezone.timedelta(days=2, hours=1),
                is_booked=True
            )
            
            appointment1 = Appointment.objects.create(
                client=self.client_user,
                lawyer=self.lawyer_user,
                date=slot1.start_time,
                status='Approved'
            )
            appointment2 = Appointment.objects.create(
                client=self.client_user,
                lawyer=another_lawyer,
                date=slot2.start_time,
                status='Approved'
            )
            
            # Test first lawyer's view
            self.client.login(email='lawyer@test.com', password='pass123')
            response = self.client.get(reverse('appointments:lawyer_dashboard') + '?status=approved')
            appointments = response.context['appointments']
            self.assertEqual(len(appointments), 1)
            self.assertEqual(appointments[0].id, appointment1.id)
            
            # Test second lawyer's view
            self.client.login(email='another_lawyer@test.com', password='pass123')
            response = self.client.get(reverse('appointments:lawyer_dashboard') + '?status=approved')
            appointments = response.context['appointments']
            self.assertEqual(len(appointments), 1)
            self.assertEqual(appointments[0].id, appointment2.id)
            
            print("  └─ ✅ Тест пройден: каждый юрист видит только свои подтвержденные записи")
        except Exception as e:
            print("  └─ ❌ Ошибка:", e)
            raise
