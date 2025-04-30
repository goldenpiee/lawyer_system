from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import LawyerProfile
from django.core.exceptions import ValidationError
from django.core import mail
from django.core.mail import EmailMessage, outbox

class AccountsBasicTest(TestCase):
    def test_create_user(self):
        print("\n[ТЕСТ] AccountsBasicTest: Проверка создания пользователя (CustomUser)")
        try:
            User = get_user_model()
            user = User.objects.create_user(
                email='testuser@example.com',
                full_name='Test User',
                phone='+79991234567',
                password='testpass'
            )
            print("  └─ Создан пользователь:", user.email)
            self.assertEqual(user.email, 'testuser@example.com')
            self.assertTrue(user.check_password('testpass'))
            print("  └─ ✅ Тест пройден: пользователь создан и пароль установлен верно")
        except Exception as e:
            print("  └─ ❌ Ошибка:", e)
            raise

    def test_login_page(self):
        print("\n[ТЕСТ] AccountsBasicTest: Проверка доступности страницы входа (login)")
        try:
            response = self.client.get(reverse('accounts:login'))
            print("  └─ Код ответа страницы входа:", response.status_code)
            self.assertEqual(response.status_code, 200)
            print("  └─ ✅ Тест пройден: страница входа доступна")
        except Exception as e:
            print("  └─ ❌ Ошибка:", e)
            raise

class AccountsAdvancedTest(TestCase):
    def setUp(self):
        print("\n[НАСТРОЙКА] AccountsAdvancedTest: создание тестовых пользователей")
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='client@test.com',
            full_name='Client User',
            phone='+79991234568',
            password='pass123'
        )
        self.lawyer = self.User.objects.create_user(
            email='lawyer@test.com',
            full_name='Lawyer User',
            phone='+79991234569',
            password='pass123'
        )
        print("  └─ Пользователь-клиент:", self.user.email)
        print("  └─ Пользователь-юрист:", self.lawyer.email)

    def test_create_lawyer_profile(self):
        print("\n[ТЕСТ] AccountsAdvancedTest: Проверка создания профиля юриста (LawyerProfile)")
        try:
            profile = LawyerProfile.objects.create(user=self.lawyer, specialization='BANKRUPTCY')
            print("  └─ Создан профиль юриста для:", profile.user.email)
            self.assertEqual(profile.user, self.lawyer)
            self.assertEqual(profile.specialization, 'BANKRUPTCY')
            print("  └─ ✅ Тест пройден: профиль юриста создан и специализация совпадает")
        except Exception as e:
            print("  └─ ❌ Ошибка:", e)
            raise

    def test_lawyer_profile_unique(self):
        print("\n[ТЕСТ] AccountsAdvancedTest: Проверка уникальности профиля юриста (LawyerProfile)")
        LawyerProfile.objects.create(user=self.lawyer, specialization='BANKRUPTCY')
        print("  └─ Первый профиль создан")
        try:
            print("  └─ Пытаемся создать второй профиль для того же пользователя (должно быть исключение)")
            profile2 = LawyerProfile(user=self.lawyer, specialization='FAMILY')
            profile2.full_clean()
            print("  └─ ❌ Ошибка: вторичный профиль создан, но ожидалось исключение")
            assert False, "Ожидалось исключение ValidationError"
        except ValidationError:
            print("  └─ ✅ Тест пройден: вторичный профиль не создан, выброшено ValidationError")
        except Exception as e:
            print("  └─ ❌ Неожиданная ошибка:", e)
            raise

    def test_send_email_function(self):
        """
        Тестирует отправку email через EmailMessage и выводит подробный результат в консоль.
        """
        subject = 'Тестовая тема'
        body = 'Тестовое сообщение для проверки отправки email.'
        from_email = 'testsender@example.com'
        to_email = ['testrecipient@example.com']

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to_email,
            headers={'Content-Type': 'text/plain; charset=utf-8'}
        )
        email.send(fail_silently=False)

        print("\n[ТЕСТ] Проверка отправки email через EmailMessage")
        print(f"  └─ Количество писем в mail.outbox: {len(mail.outbox)}")
        if mail.outbox:
            msg = mail.outbox[0]
            print(f"  └─ Тема: {msg.subject}")
            print(f"  └─ Отправитель: {msg.from_email}")
            print(f"  └─ Получатели: {msg.to}")
            print(f"  └─ Тело письма: {msg.body}")
            print(f"  └─ Headers: {msg.extra_headers}")
            assert msg.subject == subject
            assert msg.body == body
            assert msg.from_email == from_email
            assert msg.to == to_email
            print("  └─ ✅ Тест отправки email успешно выполнен")
        else:
            print("  └─ ❌ Письмо не найдено в mail.outbox!")
            self.fail("Письмо не отправлено")
