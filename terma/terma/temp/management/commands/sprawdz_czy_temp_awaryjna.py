import os
import time
import requests
from django.core.management.base import BaseCommand, CommandError
from temp.models import Sample, Opcje, Termometr, Przekaznik
from django.core.mail import send_mail
import RPi.GPIO as GPIO

class Command(BaseCommand):
    help = 'Wysyła wiadomość jak temperatura przekroczy 70 stopni'
    def handle(self, *args, **options): 
        t1 = Termometr.objects.get(nazwa='niski')
        t2 = Termometr.objects.get(nazwa='średni')
        t3 = Termometr.objects.get(nazwa='wysoki')
        o = Opcje.objects.get(aktywne=True)
        temp1 = t1.read_temp()
        temp2 = t2.read_temp()
        temp3 = t3.read_temp()
        print(temp1, temp2, temp3)
        ta = o.temp_awaryjna
        if temp1 > ta or temp2 > ta or temp3 > ta:
            # najpierw email
            subject = 'Awaria! Temp: n{t1} s{t2} w{t3}'.format(t1=temp1, t2=temp2, t3=temp3)
            message = 'temperatura 1: {temp1}\ntemperatura 2: {temp2}\ntemperatura 3: {temp3}'
            message = message.format(temp1=temp1, temp2=temp2, temp3=temp3)

            for x in range(60):
                try:
                    r = requests.get('https://www.google.pl/', timeout=20)
                    if r:
                        print('ok')
                        send_mail(
                            subject,
                            message,
                            'info@biglodl.pl',
                            ['macbilicki@gmail.com'],
                            fail_silently=True,
                            )
                        break
                    else:
                        print('brak internetu')
                except requests.exceptions.ConnectionError:
                        print('brak połączenia z wifi lub błąd')
                time.sleep(10)

            # potem na wszelki reset pinów
            g0 = Przekaznik.objects.get(nazwa='g0')
            g1 = Przekaznik.objects.get(nazwa='g1')
            g2 = Przekaznik.objects.get(nazwa='g2')
            g3 = Przekaznik.objects.get(nazwa='g3')
            pompa = Przekaznik.objects.get(nazwa='pompa')
            wszytko = [g0, g1, g2, g3, pompa]
            for g in wszytko:
                g.setup()
                g.off()
            GPIO.cleanup()
            # a na koniec na wszelki wypadek restart
            os.system('sudo /bin/systemctl reboot')
