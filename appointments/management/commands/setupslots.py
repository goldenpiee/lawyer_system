from django.core.management.base import BaseCommand
from appointments.utils import setup_slots

class Command(BaseCommand):
    help = 'Удаляет старые и создает новые слоты для юриста'

    def handle(self, *args, **kwargs):
        setup_slots()
        self.stdout.write(self.style.SUCCESS('Слоты обновлены'))
