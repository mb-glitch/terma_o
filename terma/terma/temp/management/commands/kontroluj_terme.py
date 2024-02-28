import os
import sys
import time
import datetime

import RPi.GPIO as GPIO
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail

from temp.models import Sample, Opcje, Termometr, Przekaznik

class Command(BaseCommand):
    help = 'Zarządza działaniem grzałek zgodnie z ustawieniami temperatur na bazie, loguje do bazy'
    def handle(self, *args, **options): 
        t1 = Termometr.objects.get(nazwa='niski')
        t2 = Termometr.objects.get(nazwa='średni')
        t3 = Termometr.objects.get(nazwa='wysoki')
        g0 = Przekaznik.objects.get(nazwa='g0')
        # g1 = Przekaznik.objects.get(nazwa='g1')
        # g2 = Przekaznik.objects.get(nazwa='g2')
        # zamieniam grzałki bo coś nawala
        g1 = Przekaznik.objects.get(nazwa='g2')
        g2 = Przekaznik.objects.get(nazwa='g1')
        g3 = Przekaznik.objects.get(nazwa='g3')
        pompa = Przekaznik.objects.get(nazwa='pompa')
        grzalki_all = [g0, g1, g2, g3]
        # inicjalizacji pinów
        g0.setup()
        g1.setup()
        g2.setup()
        g3.setup()
        pompa.setup()

        while True:
            try:
                o = Opcje.objects.get(aktywne=True)
                s = Sample(
                        data=datetime.datetime.now(),
                        t1=t1.read_temp(), 
                        t2=t2.read_temp(), 
                        t3=t3.read_temp(),
                        g0=g0.wlaczony,
                        g1=g1.wlaczony,
                        g2=g2.wlaczony,
                        g3=g3.wlaczony,
                        pompa=pompa.wlaczony,
                        )
                t = None
                tz = None
                grzalki = []
                
                def off():
                    for g in grzalki_all:
                        g.off()
                    if o.turbo:
                        o.turbo = False
                        o.save()
                
                def on():
                    for g in grzalki:
                        g.on()

                if s.taryfa2():
                    grzalki = [g1]
                    g0.off()  # zabezpieczenie przed włączeniem obu grzałek na jednej fazie
                    tz = o.temp_normalna  # normalna temp grzania
                    t = s.t2  # temperatura ze środkowego termometru
                else:
                    grzalki = [g0]  # włączam grzałkę w połowie zbiornika
                    g1.off()  # zabezpieczenie przed włączeniem obu grzałek na jednej fazie
                    tz = o.temp_minimalna  # minimalna temp grzania
                    t = s.t3  # temperatura ze górnego termometru
                if o.turbo:
                    s.turbo = True
                    grzalki += [g2, g3]
                else:
                    g2.off()
                    g3.off()
                if o.wakacje > s.data:
                    s.wakacje = True
                    grzalki = []
                    off()
                    pompa.off()
                ta = o.temp_awaryjna
                s.tz = tz
                test = s.temperatura(tz, o.histereza, t)
                if s.t1 > ta or s.t2 > ta or s.t3 > ta:
                    s.awaria = True
                    grzalki = []
                    off()
                elif test:
                    on()
                elif test is None:
                    pass  # zachowuje stan włączony/wyłączony (mam nadzieję)
                else:
                    off()
                s.save()
                time.sleep(10)

            except KeyboardInterrupt:
                off()
                GPIO.cleanup()
                sys.exit(0)
            except Exception as e:
                off()
                print(e)
                GPIO.cleanup()
                sys.exit(1)
            except:
                off()
                GPIO.cleanup()
                sys.exit(1)
            

