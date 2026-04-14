from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from appointments.utils import send_email_notification
from appointments.models import Appointment
from .forms import (
    RegistrationForm, EmailAuthenticationForm, ProfileEditForm,
    PasswordResetRequestForm, PasswordResetConfirmForm, ClientDocumentForm
)
from .models import ClientDocument

User = get_user_model()

def home(request):
    return render(request, 'home.html', {'message': 'Добро пожаловать!'})

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        if email and phone:
            with transaction.atomic():
                User.objects.filter(is_active=False).filter(Q(email=email) | Q(phone=phone)).delete()
                
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            code = get_random_string(6, allowed_chars='0123456789')
            request.session['registration_email'] = user.email
            request.session['registration_code'] = code
            send_email_notification('Код подтверждения регистрации', f'Ваш код: {code}', user.email)
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
            user = User.objects.filter(email=email).first()
            if user:
                user.is_active = True
                user.save()
                del request.session['registration_code']
                del request.session['registration_email']
                messages.success(request, 'Email подтвержден. Теперь вы можете войти.')
                return redirect('accounts:login')
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
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user:
                login(request, user)
                return redirect(request.GET.get('next', 'home'))
            messages.error(request, 'Неверный email или пароль.')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def edit_profile(request):
    profile_form = ProfileEditForm(instance=request.user)
    document_form = ClientDocumentForm()
    
    if request.method == 'POST':
        if 'update_profile' in request.POST: 
            profile_form = ProfileEditForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Профиль обновлен.')
                return redirect('accounts:edit_profile') 
        elif 'upload_document' in request.POST: 
            document_form = ClientDocumentForm(request.POST, request.FILES)
            if document_form.is_valid():
                new_document = document_form.save(commit=False)
                new_document.client = request.user
                new_document.save()
                messages.success(request, 'Документ загружен.')
                return redirect('accounts:edit_profile') 
                
    return render(request, 'accounts/edit_profile.html', {
        'profile_form': profile_form,
        'document_form': document_form,
        'general_documents': request.user.general_documents.all(), 
    })

def password_reset_request(request):
    code_sent = False
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                code = get_random_string(6, allowed_chars='0123456789')
                request.session['reset_email'] = email
                request.session['reset_code'] = code
                send_email_notification('Сброс пароля', f'Код: {code}', email)
                messages.success(request, "Код отправлен.")
                return redirect('accounts:password_reset_confirm')
            form.add_error('email', 'Email не найден.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'registration/password_reset_request.html', {'form': form})

def password_reset_confirm(request):
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['code'] == request.session.get('reset_code'):
                user = User.objects.filter(email=request.session.get('reset_email')).first()
                if user:
                    user.set_password(form.cleaned_data['new_password1'])
                    user.save()
                    request.session.pop('reset_code', None)
                    request.session.pop('reset_email', None)
                    messages.success(request, 'Пароль изменён.')
                    return redirect('accounts:login')
            form.add_error('code', 'Неверный код.')
    else:
        form = PasswordResetConfirmForm()
    return render(request, 'registration/password_reset_confirm.html', {'form': form})

@login_required
def client_profile(request):
    if request.method == 'POST' and 'upload_general_document' in request.POST:
        form = ClientDocumentForm(request.POST, request.FILES, instance=ClientDocument(client=request.user))
        if form.is_valid():
            form.save() 
            messages.success(request, 'Документ загружен.')
            return redirect('accounts:client_profile')

    return render(request, 'accounts/client_profile.html', {
        'user': request.user,
        'appointments': Appointment.objects.filter(client=request.user).select_related('lawyer').order_by('-date'),
        'general_documents': request.user.general_documents.all(),
        'general_document_form': ClientDocumentForm(),
    })

class CustomLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return self.request.GET.get('next', reverse_lazy('home'))

@login_required
def delete_general_document(request, document_id):
    if request.method == 'POST':
        document = get_object_or_404(ClientDocument, id=document_id, client=request.user)
        document.document.delete(save=False)
        document.delete() 
        messages.success(request, 'Документ удален.')
    return redirect('accounts:edit_profile')