from django import forms
from .models import CalendarSlot
from django.forms import DateTimeInput
from .models import AppointmentDocument

class CalendarSlotForm(forms.ModelForm):
    class Meta:
        model = CalendarSlot
        fields = ['start_time', 'end_time', 'lawyer']
        widgets = {
            'start_time': DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'lawyer': forms.Select(attrs={'class': 'form-control'})
        }
class AppointmentDocumentForm(forms.ModelForm):
    class Meta:
        model = AppointmentDocument
        fields = ['document', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Краткое описание файла (необязательно)'}),
            'document': forms.FileInput(attrs={'class': 'form-control'})
        }