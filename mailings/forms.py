from django import forms
from .models import Mailing
from clients.models import Client


class MailingForm(forms.Form):
    mailing = forms.ModelChoiceField(queryset=Mailing.objects.all(), label='Рассылка')
    clients = forms.ModelMultipleChoiceField(queryset=Client.objects.all(), label='Клиенты', required=False)
    send_to_all = forms.BooleanField(required=False, label='Отправить всем клиентам')
