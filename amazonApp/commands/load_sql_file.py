from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError
import os


class Command(BaseCommand):
    help = 'Custom database setup command'

    def handle(self, *args, **options):
        try:
            # Run Django migrations
            self.stdout.write(self.style.SUCCESS('Running migrations...'))
            os.system('python manage.py migrate')

            # Execute SQL commands
            self.stdout.write(self.style.SUCCESS('Executing SQL commands...'))
            with connection.cursor() as cursor:
                with open('app/data_amazon.sql', 'r') as sql_file:
                    cursor.execute(sql_file.read())

            self.stdout.write(self.style.SUCCESS('Database setup complete'))

        except OperationalError as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))