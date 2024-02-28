import time
import requests
from django.core.management.base import BaseCommand, CommandError
from temp.models import Sample
from django.core.mail import send_mail


class Command(BaseCommand):
    help = 'Wysyła wiadomość codziennie w określonych godzinach z informacją co się dzieje w termie'


    def handle(self, *args, **options): 
        s = Sample.objects.order_by('-data')[0]
        subject = '{d} Temp: n{t1} s{t2} w{t3}'.format(d=s, t1=s.t1/1000, t2=s.t2/1000, t3=s.t3/1000)
        message = requests.get('http://localhost/')
        
        for x in range(600):
            try:
                r = requests.get('https://www.google.pl/', timeout=20)
                if r:
                    print('ok')
                    send_mail(
                        subject,
                        None,  # pusty tekst wiadomości 
                        'info@biglodl.pl',
                        ['macbilicki@gmail.com',],
                        fail_silently=True,
                        html_message=message.text,
                        )
                    break
                else:
                    print('brak internetu')
            except requests.exceptions.ConnectionError:
                    print('brak połączenia z wifi lub błąd')
            time.sleep(10)
