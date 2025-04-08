from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from mail_messages.models import Message


class Command(BaseCommand):
    help = 'Создание группы Менеджеры и назначение прав'

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name='Менеджеры')

        permissions = [
            ('client', 'client', 'view_client'),
            ('mailing', 'mailing', 'view_mailing'),
            ('users', 'user', 'view_user'),
            ('users', 'user', 'block_user'),
            ('mail_messages', 'message', 'add_message'),
            ('mail_messages', 'message', 'view_message'),
            ('mail_messages', 'message', 'change_message'),
            ('mail_messages', 'message', 'delete_message'),
            ('mailing', 'mailing', 'add_mailing'),
            ('mailing', 'mailing', 'view_mailing'),
            ('mailing', 'mailing', 'change_mailing'),
            ('mailing', 'mailing', 'delete_mailing'),
        ]

        for app_label, model, codename in permissions:
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            permission = Permission.objects.get(codename=codename, content_type=content_type)
            group.permissions.add(permission)

        group.save()
        self.stdout.write(self.style.SUCCESS("Группа 'Менеджеры' создана/обновлена с необходимыми правами."))




