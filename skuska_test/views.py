from django.shortcuts import render
from django.http import HttpResponseRedirect
from glob import glob
from django.template.context_processors import csrf
from .models import Result

import os
import json
import random
import ast

# Create your views here.
def metadata(request):
    c = {}
    c.update(csrf(request))
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_files = glob(os.path.join(BASE_DIR,'static','testy','*.json'))
    testy = []
    for test_file in test_files:
        with open(test_file) as t:
            test = json.load(t)
        testy.append([test_file,test["nazov"]])
    return render(request,'metadata.html',{'testy':testy})

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

    vysledok = {}
    for otazka in otazky:
        vysledok[otazka] = []
        odpovede = request.POST.getlist(otazka)
        for odpoved in odpovede:
            odpoved = ast.literal_eval(odpoved)
            vysledok[otazka].append(odpoved)
            result.body += odpoved[1]

    with open(result.test_subor) as f:
        test = json.load(f)

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
