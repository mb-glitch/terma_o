import datetime
from django.core.management.base import BaseCommand, CommandError
from temp.models import Sample


class Command(BaseCommand):
    help = 'Usuwa dane starsze niż miesiąc'

    def handle(self, *args, **options): 
        s = Sample.objects.all()
        miesiac = datetime.datetime.now() - datetime.timedelta(days=30)
        s = s.filter(data__lte=miesiac)
        s.delete()
