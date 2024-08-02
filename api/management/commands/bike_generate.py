# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from api.models import Bike
import random


class Command(BaseCommand):
    help = 'Генерация новых велосипедов (по умолчанию: 1000)'

    def add_arguments(self, parser):
        parser.add_argument(
            '-a',
            '--amount',
            type=int,
            default=1000,
            help='Количество генерируемых велосипедов (по умолчанию: 1000)'
        )

    def handle(self, *args, **options):
        bike_amount = options['amount']
        bike_error = 0

        for i in range(1, bike_amount + 1):
            try:
                new_bike, created = Bike.objects.get_or_create(
                    name=f'Bike {i}',
                    defaults={
                        'status': Bike.STATUS_AVAILABLE,
                        'rental_price': round(random.uniform(10, 100), 2)
                    }
                )
                if created:
                    if i % 100 == 0:
                        self.stdout.write(self.style.SUCCESS(f'Велосипедов сгенерировано {i}'))
            except Exception as e:
                bike_error += 1
                self.stdout.write(self.style.ERROR(f'Ошибка при генерации велосипеда {i}: {str(e)}'))

        if bike_error > 0:
            self.stdout.write(self.style.WARNING(f'{bike_error} Ошибок при генерации велосипедов.'))
