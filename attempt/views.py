from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from clients.views import is_manager
from .models import Mailing
from django.contrib import messages

class MailingSendView(LoginRequiredMixin, View):
    def get(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        if not (mailing.owner == request.user or is_manager(request.user)):
            raise PermissionDenied("У вас нет прав на отправку этой рассылки.")

        try:
            send_mailing(mailing.id)  # Вызываем функцию отправки рассылки
            messages.success(request, f"Рассылка '{mailing.name}' успешно запущена.")
        except ValueError as e:
            messages.error(request, str(e))  # Отображаем сообщение об ошибке
        except Exception as e:
            messages.error(request, "Произошла ошибка при отправке рассылки.")  # Отображаем сообщение об ошибке
            # Тут можно добавить логирование ошибки
        return redirect('mailing:mailing_list')  # Перенаправляем пользователя



