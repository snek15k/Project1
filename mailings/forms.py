from django import forms
from .models import Mailing


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = fields = ['name', 'message', 'clients']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Select(attrs={'class': 'form-control'}),
            'clients': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
