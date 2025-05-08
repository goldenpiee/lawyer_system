from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db import models
from django.db.models import Q
from django.http import HttpResponseForbidden 
from .forms import (
    RegistrationForm, EmailAuthenticationForm, ProfileEditForm,
    PasswordResetRequestForm, PasswordResetConfirmForm, ClientDocumentForm, ClientDocument
)

def home(request):
    return render(request, 'home.html', {'message': 'Добро пожаловать!'})

def register(request):
    if request.method == 'POST':
        # Получаем email и phone до создания формы
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        if email and phone:
            User = get_user_model()
            with transaction.atomic():
                User.objects.filter(is_active=False).filter(
                    Q(email=email) | Q(phone=phone)
                ).delete()
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            code = get_random_string(6, allowed_chars='0123456789')
            request.session['registration_email'] = user.email
            request.session['registration_code'] = code
            
            email = EmailMessage(
                subject='Код подтверждения регистрации',
                body=f'Ваш код для подтверждения регистрации: {code}',
                from_email='Юридические услуги по банкротству <matrica646@gmail.com>',
                to=[user.email],
                headers={'Content-Type': 'text/plain; charset=utf-8'}
            )
            email.send(fail_silently=False)
            
            messages.success(request, 'Код отправлен на ваш email.')
            return redirect('accounts:confirm_email')
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/registration.html', {'form': form})

def confirm_email(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        email = request.session.get('registration_email')
        session_code = request.session.get('registration_code')
        if code == session_code and email:
            user = get_user_model().objects.filter(email=email).first()
            if user:
                user.is_active = True
                user.save()
                # Очищаем сессию
                request.session.pop('registration_code', None)
                request.session.pop('registration_email', None)
                messages.success(request, 'Email подтвержден. Теперь вы можете войти.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Пользователь не найден.')
        else:
            messages.error(request, 'Неверный код подтверждения.')
    return render(request, 'registration/confirm_email.html')

@login_required
def profile_redirect(request):
    if request.user.is_staff:
        return redirect('appointments:lawyer_dashboard')
    return redirect('accounts:client_profile')

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next')
                return redirect(next_url if next_url else 'home')
            else:
                messages.error(request, 'Неверный email или пароль.')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def edit_profile(request):
    profile_form = ProfileEditForm(instance=request.user)
    # Инициализируем форму загрузки документа для GET запроса
    # и если POST был для другой формы
    document_form = ClientDocumentForm()
    
    # Получаем существующие документы для отображения
    general_documents = request.user.general_documents.all()


    if request.method == 'POST':
        # Определяем, какая форма была отправлена
        if 'update_profile' in request.POST: # Предположим, у кнопки формы профиля есть name="update_profile"
            profile_form = ProfileEditForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Ваш профиль успешно обновлен.')
                return redirect('accounts:edit_profile') # Остаемся на странице редактирования
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме профиля.')
        
        elif 'upload_document' in request.POST: # У кнопки загрузки будет name="upload_document"
            # Передаем request.user в instance, чтобы client заполнился автоматически
            document_form = ClientDocumentForm(request.POST, request.FILES)
            if document_form.is_valid():
                new_document = document_form.save(commit=False)
                new_document.client = request.user # Устанавливаем клиента
                new_document.save()
                messages.success(request, f'Документ "{new_document.title}" успешно загружен.')
                return redirect('accounts:edit_profile') # Остаемся на странице редактирования
            else:
                # Сообщаем об ошибке и document_form с ошибками будет передан в контекст
                error_list = []
                for field, errors in document_form.errors.items():
                    for error in errors:
                        error_list.append(f"{document_form.fields[field].label if field != '__all__' else 'Форма'}: {error}")
                messages.error(request, "Ошибка загрузки документа: " + " ".join(error_list))

    context = {
        'profile_form': profile_form,
        'document_form': document_form, # Передаем форму загрузки
        'general_documents': general_documents, # Передаем существующие документы
    }
    return render(request, 'accounts/edit_profile.html', context)

def password_reset_request(request):
    code_sent = False
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = get_user_model().objects.filter(email=email).first()
            if user:
                code = get_random_string(6, allowed_chars='0123456789')
                request.session['reset_email'] = email
                request.session['reset_code'] = code
                email_message = EmailMessage(
                    subject='Код для сброса пароля',
                    body=f'Ваш код для сброса пароля: {code}',
                    from_email='Юридические услуги по банкротству <matrica646@gmail.com>',
                    to=[email],
                    headers={'Content-Type': 'text/plain; charset=utf-8'}
                )
                email_message.send(fail_silently=False)
                messages.success(request, "Код отправлен на ваш email.")
                return redirect('accounts:password_reset_confirm')
            else:
                form.add_error('email', 'Пользователь с таким email не найден.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'registration/password_reset_request.html', {'form': form})

def password_reset_confirm(request):
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            password = form.cleaned_data['new_password1']
            session_code = request.session.get('reset_code')
            email = request.session.get('reset_email')
            if code == session_code and email:
                user = get_user_model().objects.filter(email=email).first()
                if user:
                    user.set_password(password)
                    user.save()
                    # Очищаем сессию
                    request.session.pop('reset_code', None)
                    request.session.pop('reset_email', None)
                    messages.success(request, 'Пароль успешно изменён. Теперь вы можете войти.')
                    return redirect('accounts:login')
                else:
                    messages.error(request, 'Пользователь не найден.')
            else:
                form.add_error('code', 'Неверный код подтверждения.')
    else:
        form = PasswordResetConfirmForm()
    return render(request, 'registration/password_reset_confirm.html', {'form': form})
@login_required
def client_profile(request):
    user = request.user
    # Получаем историю записей (если это из appointments, то импортировать Appointment)
    # appointments = user.client_appointments.all().order_by('-date')
    # Лучше передавать Appointment из приложения appointments, если логика специфична
    from appointments.models import Appointment # Пример импорта
    appointments = Appointment.objects.filter(client=user).order_by('-date')


    general_documents = user.general_documents.all() # Получаем общие документы клиента
    general_document_form = ClientDocumentForm()

    # Логика для вычисления can_cancel для каждой записи
    from django.utils import timezone
    from datetime import timedelta
    for appointment in appointments:
        can_cancel_deadline = appointment.date - timedelta(hours=24)
        appointment.can_cancel = (appointment.status in ['Pending', 'Approved']) and \
                                 (timezone.now() < can_cancel_deadline)
        # Также загружаем документы для каждой записи
        appointment.attached_documents = appointment.documents.all()


    if request.method == 'POST':
        # Различаем, какая форма была отправлена, если их несколько
        if 'upload_general_document' in request.POST: # Предполагаем, что у кнопки submit есть name="upload_general_document"
            general_document_form = ClientDocumentForm(request.POST, request.FILES)
            if general_document_form.is_valid():
                doc = general_document_form.save(commit=False)
                doc.client = user
                doc.save()
                messages.success(request, f"Общий документ '{doc.document.name.split('/')[-1]}' успешно загружен.")
                return redirect('accounts:client_profile') # Перезагружаем страницу
            else:
                messages.error(request, "Ошибка при загрузке общего документа.")
        # Здесь может быть другая логика POST, если есть другие формы на странице

    context = {
        'user': user,
        'appointments': appointments,
        'general_documents': general_documents,
        'general_document_form': general_document_form,
        # 'profile_edit_form': ProfileEditForm(instance=user) # Если форма редактирования тоже здесь
    }
    return render(request, 'accounts/client_profile.html', context)

class CustomLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, 'Неверный email или пароль. Попробуйте снова.')
        return super().form_invalid(form)
@login_required
def delete_general_document(request, document_id):
    document = get_object_or_404(ClientDocument, id=document_id)

    # Проверка, что текущий пользователь является владельцем документа
    if document.client != request.user:
        messages.error(request, "У вас нет прав для удаления этого документа.")
        return redirect('accounts:edit_profile') # или client_profile

    if request.method == 'POST':
        document_title = document.title # Сохраняем название для сообщения
        try:
            document.document.delete(save=True) # Удаляем файл с диска
            document.delete() # Удаляем запись из БД
            messages.success(request, f'Документ "{document_title}" успешно удален.')
        except Exception as e:
            messages.error(request, f'Ошибка при удалении документа: {e}')
        return redirect('accounts:edit_profile') # Возвращаемся на страницу редактирования
    messages.warning(request, "Для удаления документа используйте POST-запрос (кнопку 'Удалить').")
    return redirect('accounts:edit_profile')