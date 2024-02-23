from django.core.management.base import BaseCommand
from amazonApp.tasks import background_task 
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Trigger Celery task'

    def handle(self, *args, **options):
        result = background_task.delay()
        task_result = result.result

        if task_result is not None:
            cache.set("exchange_rates", task_result, timeout=None)
            self.stdout.write(self.style.SUCCESS('Exchange rates have been uploaded'))
        else:
            self.stderr.write(self.style.ERROR('Exchange rates have not been uploaded'))