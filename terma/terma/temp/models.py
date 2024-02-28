import RPi.GPIO as GPIO
from django.db import models


class Termometr(models.Model):
    #termometr_1 = '/sys/bus/w1/devices/28-00000a39138b/w1_slave'
    #termometr_2 = '/sys/bus/w1/devices/28-00000a3966eb/w1_slave'
    #termometr_3 = '/sys/bus/w1/devices/28-00000a3a5da3/w1_slave'
    nazwa = models.CharField(max_length=10)
    adress = models.FilePathField(path='/sys/bus/w1/devices/', allow_folders=True,  max_length=40)

    def __str__(self):
        return self.nazwa

    @property
    def path(self):
        return '{adress}/w1_slave'.format(adress=self.adress)

    def read_temp(self):
        lines = None
        try:
            with open(self.path, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            lines = None
            return False
        try:
            lines[0].find('YES')
        except Exception as e:
            lines = None
            return False
        try:
            temp_output = lines[1].find('t=')
            if temp_output != -1:
                temp = lines[1].strip()[temp_output+2:]
                temp = int(temp)
                return temp
        except Exception as e:
            lines = None
            return False


class Przekaznik(models.Model):
    #g0 = (25)  # g0 i g1 na jednej fazie - nie właczaj razem
    #g1 = (18)
    #g2 = (23)
    #g3 = (24)
    #pompa = (12) 
    nazwa = models.CharField(max_length=10)
    pin = models.IntegerField()

    def __str__(self):
        return self.nazwa

    def setup(self):
        print('setup przekaźnika {nazwa}-{pin}'.format(nazwa=self.nazwa, pin=self.pin))
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, 1)

    @property
    def wlaczony(self):
        return bool(not GPIO.input(self.pin))

    def on(self):
        if not self.wlaczony:
            GPIO.output(self.pin, 0)
            print('właczam przekaźnik {nazwa}'.format(nazwa=self.nazwa))
    
    def off(self):
        if self.wlaczony:
            GPIO.output(self.pin, 1)
            print('wyłaczam przekaźnik {nazwa}'.format(nazwa=self.nazwa))


class Opcje(models.Model):
    aktywne = models.BooleanField(default=False)
    temp_normalna = models.IntegerField()
    temp_minimalna = models.IntegerField()
    temp_awaryjna = models.IntegerField()
    histereza = models.IntegerField()
    turbo = models.BooleanField(default=False)
    wakacje = models.DateTimeField('wakacje do')

    def __str__(self):
        a = None
        if self.aktywne:
            a = 'Aktywne'
        return a

class Sample(models.Model):
    data = models.DateTimeField('data pomiaru')
    tz = models.IntegerField(default=0)  # temperatura zadana
    t1 = models.IntegerField()  # niski
    t2 = models.IntegerField()  # środkowy
    t3 = models.IntegerField()  # wysoki
    g0 = models.BooleanField(default=False)  # grzałka w połowie zbiornika
    g1 = models.BooleanField(default=False)  # 1/3
    g2 = models.BooleanField(default=False)  # 2/3
    g3 = models.BooleanField(default=False)  # 3/3
    awaria = models.BooleanField(default=False)
    pompa = models.BooleanField(default=False)
    turbo = models.BooleanField(default=False)
    wakacje = models.BooleanField(default=False)

    def __str__(self):
        return self.data.strftime('%Y-%m-%d %H:%M:%S')

    def wlaczyc_pompe(self):
        hour = self.data.hour
        temp = self.t2
        if hour >= 22 and temp > 40000:
            return True
        else:
            return False            

    def taryfa2(self):
        hour = self.data.hour
        # II taryfa
        if hour >= 13 and hour < 15:
            return True
        elif hour >= 22 or hour < 6:
            return True
        else:
            return False

    def temperatura(self, temp_zadana, histereza, temp_zmierzona):
        """temperatura * 1000, czyli taka jaką domyślnie dają czujniki"""
        t = temp_zmierzona
        tz = temp_zadana
        t_min = tz - histereza
        t_max = tz + histereza
        print('tz={tz}     t1={t1} t2={t2} t3={t3}'.format(
            tz=self.tz/1000,
            t1=self.t1/1000,
            t2=self.t2/1000,
            t3=self.t3/1000,
            ))
        if t < t_min:
            print('włączyć grzałki')
            return True
        if t > t_max:
            print('wyłączyć grzałki')
            return False


    class Meta:

        ordering = ['-data']
