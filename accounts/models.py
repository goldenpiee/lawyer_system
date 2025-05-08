from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from django.core.exceptions import ValidationError # Для валидации
from django.urls import reverse 
import os

class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        if not phone:
            raise ValueError('Телефон обязателен')
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            full_name=full_name,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, phone, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(
        "Email",
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',
                message="Некорректный формат email"
            )
        ]
    )
    full_name = models.CharField("ФИО", max_length=150)
    phone = models.CharField(
        "Телефон",
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+?7?\d{10}$',
                message="Телефон должен быть в формате +7XXXXXXXXXX"
            )
        ]
    )

    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self): 
        return self.full_name.split(' ')[0] if self.full_name else ''

    def get_absolute_url(self):
        if hasattr(self, 'lawyerprofile') and self.lawyerprofile is not None:
            return reverse('appointments:lawyer_dashboard')
        else:
            return reverse('accounts:client_profile')

class LawyerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    specialization = models.CharField(
        "Специализация",
        max_length=100,
        choices=[
            ('BANKRUPTCY', 'Банкротство'),
            ('FAMILY', 'Семейное право'),
            ('CRIMINAL', 'Уголовное право'),
        ],
        default='BANKRUPTCY'
    )
    office_address = models.CharField(
        "Адрес офиса",
        max_length=200,
        default='г. Сегежа, ул. Ленина 19а'
    )

    def clean(self):
        if LawyerProfile.objects.exclude(pk=self.pk).filter(user=self.user).exists():
            from django.core.exceptions import ValidationError
            raise ValidationError("Этот пользователь уже имеет профиль юриста.")

    def __str__(self):
        return f'Lawyer: {self.user.email}'
class ClientDocument(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='general_documents',
        on_delete=models.CASCADE
    )
    # === НОВОЕ ПОЛЕ ===
    title = models.CharField(
        "Название документа",
        max_length=150,
        help_text="Придумайте короткое и понятное название для этого документа (например, 'Скан паспорта', 'Договор аренды')."
    )
    # ==================
    document = models.FileField(
        upload_to='client_general_documents/%Y/%m/%d/',
        verbose_name="Файл документа"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(
        max_length=255,
        blank=True, # Описание остается необязательным
        verbose_name="Краткое описание (необязательно)"
    )

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Общий документ клиента"
        verbose_name_plural = "Общие документы клиентов"

    def __str__(self):
        # Обновляем __str__ для использования нового поля title
        return f"{self.title} (Клиент: {self.client.email})"

    def clean(self):
        super().clean()
        # Проверка, что title не пустой (хотя CharField по умолчанию и так это делает,
        # но можно добавить кастомное сообщение)
        if not self.title.strip(): # .strip() чтобы убрать пробелы по краям
            raise ValidationError({'title': 'Название документа не может быть пустым или состоять только из пробелов.'})

    def filename(self):
        return os.path.basename(self.document.name)
