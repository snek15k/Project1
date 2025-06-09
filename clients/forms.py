from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["email", "full_name", "comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Введите дополнительную информацию"}
            ),
        }
        help_texts = {"comment": "Введите дополнительную информацию о получателе"}

    def clean(self):
        cleaned_data = super(ClientForm, self).clean()
        email = cleaned_data.get("email")
        full_name = cleaned_data.get("full_name")

        if not email:
            raise forms.ValidationError("Поле Email обязательно для заполнения")
        if not full_name:
            raise forms.ValidationError("Поле ФИО обязательно для заполнения")

        if email:
            owner = self.instance.owner if self.instance.pk else None
            if (
                owner is not None
                and Client.objects.filter(email=email, owner=owner).exists()
            ):
                raise forms.ValidationError(
                    "Этот email уже используется другим получателем"
                )

        return cleaned_data
