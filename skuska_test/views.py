from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template.context_processors import csrf
from .models import Result
from skuska_admin.models import Test

import os
import json
import random
import ast

# Create your views here.
def metadata(request):
    aktivne_testy = Test.objects.filter(active=True)
    if len(aktivne_testy) != 0:
        c = {}
        c.update(csrf(request))
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        testy = []
        for test in aktivne_testy:
            testy.append([os.path.join(BASE_DIR,'static',test.test_subor),test.__str__()])
        return render(request,'metadata.html',{'testy':testy})

    else:
        return render(request,'notests.html')

def test(request):
    c = {}
    c.update(csrf(request))
    student = request.POST.get('student')
    with open(request.POST.get('test')) as f:
        test = json.load(f)
    skuska = {}
    skuska["student"] = student
    skuska["test"] = [request.POST.get('test'),test["nazov"]]
    skuska["otazky"] = []
    random.shuffle(test["sekcie"])
    for sekcia in test["sekcie"]:
        for otazka in random.sample(sekcia["otazky"],sekcia["pocet_otazok"]):
            random.shuffle(otazka["odpovede"])
            if "obrazok" in otazka:
                otazka["obrazok"] = "{}{}".format("testy/obrazky/",otazka["obrazok"])
            skuska["otazky"].append(otazka)
    return render(request,'test.html',{'skuska':skuska})

def vysledok(request):
    result = Result()
    result.student = request.POST.get('student')
    result.test_subor = request.POST.get('test_subor')
    result.test_nazov = request.POST.get('test_nazov')
    result.body = 0

    otazky = []
    for item in request.POST:
        if item != 'csrfmiddlewaretoken' and item != 'student' and item != 'test_nazov' and item != 'test_subor':
            otazky.append(item)

    with open(result.test_subor) as f:
        test = json.load(f)

    print(otazky)
    vysledok = {}
    for otazka in otazky:
        vysledok[otazka] = []
        odpovede = request.POST.getlist(otazka)

        spravne = 0
        for odpoved in odpovede:
            odpoved = ast.literal_eval(odpoved)
            vysledok[otazka].append(odpoved)
            spravne += odpoved[1]

        poc_spravnych = 0
        for s in test["sekcie"]:
            for o in s["otazky"]:
                if o["id"] == int(otazka):
                    for odp in o["odpovede"]:
                        poc_spravnych += odp[1]

        if spravne == poc_spravnych and len(vysledok[otazka]) == poc_spravnych:
            result.body += o["body"][0]
        else:
            result.body += o["body"][1]

    result.odpovede = vysledok

    if "vyhovel" in test["znamky"]:
        if result.body >= test["znamky"]["vyhovel"]:
            result.znamka = "vyhovel(a)"
        else:
            result.znamka = "nevyhovel(a)"
    else:
        for znamka in ['A','B','C','D','E']:
            if result.body >= test["znamky"][znamka]:
                result.znamka = znamka
                break

    result.save()

    if result.znamka != 'Fx' and result.znamka != "nevyhovel(a)":
        return render(request,'uspech.html',{'znamka':result.znamka,'body':result.body})
    else:
        return render(request,'neuspech.html',{'znamka':result.znamka,'body':result.body})
