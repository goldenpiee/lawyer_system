from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import ClientDocument


User = get_user_model()
class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'email', 
            'full_name', 
            'phone', 
            'password1', 
            'password2'
        ]

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control profile-edit-field'}),
            'phone': forms.TextInput(attrs={'class': 'form-control profile-edit-field'}),
        }

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'autofocus': True})
    )

    class Meta:
        model = User
        fields = ['email', 'password']

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))

class PasswordResetConfirmForm(forms.Form):
    code = forms.CharField(label="Код из email", max_length=6, widget=forms.TextInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label="Повторите новый пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data
class ClientDocumentForm(forms.ModelForm):
    class Meta:
        model = ClientDocument
        fields = ['document', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Описание (необязательно)'}),
            'document': forms.FileInput(attrs={'class': 'form-control form-control-sm'})
        }