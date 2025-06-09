from django.core.management.base import BaseCommand

from mailings.models import Mailing
from mailings.services import send_mailing


class Command(BaseCommand):
    help = "Отправка запланированных рассылок"

    def handle(self, *args, **options):
        mailings = Mailing.objects.filter(status="started", is_active=True)
        for mailing in mailings:
            send_mailing(mailing.id)
