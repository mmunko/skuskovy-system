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
        testy = []
        for test in aktivne_testy:
            testy.append([test.id,test.__str__()])
        return render(request,'metadata.html',{'testy':testy})

    else:
        return render(request,'notests.html')

def test(request):
    c = {}
    c.update(csrf(request))
    student = request.POST.get('student')
    test_id = int(request.POST.get('test'))
    test_file = Test.objects.filter(id=test_id).values('test_subor')
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_file = os.path.join(BASE_DIR,'static','testy',test_file[0]["test_subor"])
    with open(test_file) as f:
        test = json.load(f)
    skuska = {}
    skuska["student"] = student
    skuska["test"] = [test_id,test["nazov"]]
    skuska["otazky"] = []
    skuska["otazky_id"] = []
    random.shuffle(test["sekcie"])
    for sekcia in test["sekcie"]:
        for otazka in random.sample(sekcia["otazky"],sekcia["pocet_otazok"]):
            skuska["otazky_id"].append(otazka["id"])
            random.shuffle(otazka["odpovede"])
            if "obrazok" in otazka:
                otazka["obrazok"] = "{}{}".format("testy/obrazky/",otazka["obrazok"])
            skuska["otazky"].append(otazka)
    return render(request,'test.html',{'skuska':skuska})

def vysledok(request):
    result = Result()
    result.student = request.POST.get('student')
    result.test = Test.objects.get(id=request.POST.get('test_id'))
    result.otazky = request.POST.get('otazky_id')
    result.body = 0

    otazky = []
    for item in request.POST:
        if item != 'csrfmiddlewaretoken' and item != 'student' and item != 'test_id' and item != 'otazky_id' and item != 'test_nazov':
            otazky.append(item)

    # test_file = Test.objects.get(id=result.test_id).values('test_subor')
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_file = os.path.join(BASE_DIR,'static','testy',result.test.test_subor)
    with open(test_file) as f:
        test = json.load(f)

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
