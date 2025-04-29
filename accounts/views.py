from django.shortcuts import render, redirect
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
from .forms import (
    RegistrationForm, EmailAuthenticationForm, ProfileEditForm,
    PasswordResetRequestForm, PasswordResetConfirmForm
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
    if request.user.is_staff:
        messages.error(request, "Редактирование личной информации доступно только клиентам.")
        return redirect('appointments:lawyer_dashboard')
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Личная информация успешно обновлена.")
            return redirect('accounts:client_profile')  # Изменено с 'appointments:client_dashboard'
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

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