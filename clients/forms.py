from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Введите дополнительную информацию'}),
        }
        help_texts = {
            'comment': 'Введите дополнительную информацию о получателе'
        }


    def clean_email(self):
        'Проверка уникальности email в рамках владельца'
        email = self.cleaned_data['email']
        owner = self.instance.owner if self.instance else self.inital.get('owner')
        if Client.objects.filter(email=email, owner=owner).exists():
            raise forms.ValidationError('Этот email уже используется другим получателем')
        return email