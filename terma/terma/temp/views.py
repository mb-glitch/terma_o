import datetime
from django.shortcuts import render
from .models import Sample

def index(request):
    context = {}
    teraz = datetime.datetime.now()
    dzis = teraz.replace(hour=0, minute=0, second=0, microsecond=0)
    wczoraj = dzis - datetime.timedelta(days=1)
    tydzien = dzis - datetime.timedelta(days=7)
    m5 = teraz - datetime.timedelta(minutes=5)
    m10 = teraz - datetime.timedelta(minutes=10)
    m20 = teraz - datetime.timedelta(minutes=20)
    m30 = teraz - datetime.timedelta(minutes=30)
    h1 = teraz - datetime.timedelta(hours=1)
    h2 = teraz - datetime.timedelta(hours=2)

    def policz_grzalki(sample_queryset):
        g0 = datetime.timedelta(seconds=0)
        g1 = datetime.timedelta()
        g2 = datetime.timedelta()
        g3 = datetime.timedelta()
        poprzedni = None
        for s in sample_queryset:
            if not poprzedni:
                poprzedni = s.data
            if s.g0:
                g0 += s.data - poprzedni
            if s.g1:
                g1 += s.data - poprzedni
            if s.g2:
                g2 += s.data - poprzedni
            if s.g3:
                g3 += s.data - poprzedni
            poprzedni = s.data
        return [g0.seconds/3600 + g0.days*24,
                g1.seconds/3600 + g1.days*24,
                g2.seconds/3600 + g2.days*24,
                g3.seconds/3600 + g3.days*24]

    l = Sample.objects.filter(data__gte=tydzien).order_by('-data')
    # suma działania na dziś
    p_dzisiaj = l.filter(data__gte=dzis).reverse()
    context['g_dzisiaj'] = policz_grzalki(p_dzisiaj)
    # suma działania na wczoraj
    p_wczoraj = l.filter(data__gte=wczoraj, data__lte=dzis).reverse()
    context['g_wczoraj'] = policz_grzalki(p_wczoraj)
    # średnia na tydzień 
    p_tydzien = l.filter(data__lte=dzis).reverse()
    srednia = []
    grzalki_tydzien = policz_grzalki(p_tydzien)
    for g in grzalki_tydzien:
        srednia.append(g/7)
    context['g_tydzien'] = srednia

    p = []
    probki = []
    p.append(l.first())
    p.append(l.filter(data__gte=m5).reverse().first())
    p.append(l.filter(data__gte=m10).reverse().first())
    p.append(l.filter(data__gte=m20).reverse().first())
    p.append(l.filter(data__gte=m30).reverse().first())
    p.append(l.filter(data__gte=h1).reverse().first())
    p.append(l.filter(data__gte=h2).reverse().first())

    for e in p:
        e.t1 = e.t1/1000
        e.t2 = e.t2/1000
        e.t3 = e.t3/1000
        probki.append(e)

    context['probki'] = probki
    return render(request, 'temp/index.html', context)

def wykres(request):
    latest_samples_list = Sample.objects.order_by('-data')[:10000]
    context = {'latest_samples_list': latest_samples_list}
    return render(request, 'temp/wykres.html', context)
