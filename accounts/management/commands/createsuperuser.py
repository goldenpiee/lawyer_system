# accounts/management/commands/create_admin_user.py

import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.conf import settings # Импортируем настройки

class Command(BaseCommand):
    help = 'Creates a superuser non-interactively using environment variables if one does not exist, tailored for CustomUser.'

    def handle(self, *args, **options):
        User = get_user_model()
        # Ваша модель использует email как USERNAME_FIELD, но явная проверка не помешает
        if User.USERNAME_FIELD != 'email':
             raise CommandError(f'Ожидалось, что USERNAME_FIELD будет "email", но найдено "{User.USERNAME_FIELD}". Адаптируйте скрипт.')


        # --- Получаем данные из переменных окружения ---
        # Важно: На Render эти переменные должны быть установлены!
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        full_name = os.environ.get('DJANGO_SUPERUSER_FULL_NAME')
        phone = os.environ.get('DJANGO_SUPERUSER_PHONE')

        # --- Проверки на наличие обязательных данных ---
        # Ваш менеджер требует email, full_name, phone и password для создания суперпользователя
        required_env_vars = {
            'DJANGO_SUPERUSER_EMAIL': email,
            'DJANGO_SUPERUSER_PASSWORD': password,
            'DJANGO_SUPERUSER_FULL_NAME': full_name,
            'DJANGO_SUPERUSER_PHONE': phone,
        }

        missing_vars = [key for key, value in required_env_vars.items() if not value]

        if missing_vars:
            raise CommandError(
                f'Отсутствуют необходимые переменные окружения для создания суперпользователя: {", ".join(missing_vars)}. '
                'Установите их на Render.'
            )

        # --- Проверка существования пользователя ---
        # Ищем пользователя по email, так как это USERNAME_FIELD и UNIQUE
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f'Суперпользователь с email "{email}" уже существует. Пропускаем создание.'))
            return # Завершаем выполнение команды успешно

        # --- Создание пользователя ---
        self.stdout.write(f"Создаю суперпользователя с email '{email}'...")
        try:
            # Вызываем create_superuser ВАШЕГО менеджера, передавая ВСЕ требуемые им поля
            # Ваш менеджер обрабатывает is_staff/is_superuser
            user = User.objects.create_superuser(
                email=email,
                password=password,
                full_name=full_name,
                phone=phone,
                # Можете добавить сюда другие необязательные поля из env vars,
                # если ваш create_superuser умеет их принимать или они попадают в **extra_fields
            )

            self.stdout.write(self.style.SUCCESS(f'Суперпользователь с email "{email}" успешно создан.'))

        except Exception as e:
            # Если что-то пошло не так в процессе создания (например, ошибка валидации телефона/email)
            raise CommandError(f'Ошибка при создании суперпользователя с email "{email}": {e}')