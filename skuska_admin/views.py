from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from .models import Test
from skuska_test.models import Result
from django.core.exceptions import ValidationError

import os
import json
import ast
import time

def login(request):
    c = {}
    c.update(csrf(request))
    return render(request,'login.html',c)

def auth_view(request):
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/manage/')
    else:
        return HttpResponseRedirect('/invalid/')

def invalid_login(request):
    return render(request,'invalid_login.html')

def logout(request):
    auth.logout(request)
    return render(request,'logout.html')

@login_required(login_url='/login/')
def manage(request):
    testy = Test.objects.all()
    return render(request,'manage.html',{'testy':testy})

@login_required(login_url='/login/')
def find_results(request):
    testy = Test.objects.all()
    return render(request,'find_results.html',{'testy':testy})

@login_required(login_url='/login/')
def view_results(request):
    test_id = request.POST.get('test')
    cas_od = request.POST.get('od')
    cas_do = request.POST.get('do')
    try:
        vysledky = Result.objects.filter(casova_peciatka__range=(cas_od,cas_do),test=test_id)
        if len(vysledky) == 0:
            return render(request,'error.html',{'text':'Zadaným kritériám nevyhovujú žiadne výsledky','navrat':'/find_results'})
        else:
            return render(request,'results.html',{'vysledky':vysledky})
    except ValidationError:
        return render(request,'error.html',{'text':'Zadaný dátum a čas nie je v správnom formáte.','navrat':'/find_results'})


@login_required(login_url='/login/')
def set_tests(request):
    running_tests = []
    for item in request.POST:
        if item != 'csrfmiddlewaretoken' and item != 'student' and item != 'test_nazov' and item != 'test_subor':
            running_tests.append(item)

    for item in Test.objects.all():
        if str(item.id) in running_tests:
            item.active = True
            new_pass = request.POST.get("{}-password".format(item.id))
            if new_pass != '':
                item.passwd = new_pass
        else:
            item.active = False
            item.passwd = None
        item.save()
    return HttpResponseRedirect('/manage/')

@login_required(login_url='/login/')
def find_test(request):
    testy = Result.objects.all()
    return render(request,'find_test.html',{'testy':testy})

@login_required(login_url='/login/')
def view_test(request):
    result_id = request.POST.get("test")
    vysledok = Result.objects.get(id=result_id)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_file = os.path.join(BASE_DIR,'static','testy',vysledok.test.test_subor)
    with open(test_file) as f:
        test = json.load(f)

    testove_otazky = ast.literal_eval(vysledok.otazky)
    otazky = []
    for sekcia in test["sekcie"]:
        for otazka in sekcia["otazky"]:
            if otazka["id"] in testove_otazky:
                if "obrazok" in otazka:
                    otazka["obrazok"] = "{}{}".format("testy/obrazky/",otazka["obrazok"])
                for odpoved in otazka["odpovede"]:
                    if len(odpoved) == 3:
                        odpoved[2] = "{}{}".format("testy/obrazky/",odpoved[2])
                    else:
                        odpoved.append("pictures/empty.png")
                otazky.append(otazka)

    for otazka in otazky:
        for odpoved in otazka["odpovede"]:
            if str(otazka["id"]) in vysledok.odpovede.keys():
                if odpoved in vysledok.odpovede[str(otazka["id"])]:
                    if odpoved[1] == 1:
                        odpoved.append('#5CD46E')
                    else:
                        odpoved.append('#FF585E')
                else:
                    if odpoved[1] == 1:
                        odpoved.append('#CEFCD5')
                    else:
                        odpoved.append('#ffffff')
            else:
                if odpoved[1] == 1:
                    odpoved.append('#CEFCD5')
                else:
                    odpoved.append('#ffffff')
    test = {}
    test["otazky"] = otazky
    test["nazov"] = vysledok.__str__()
    test["vysledok"] = "body: {} / výsledok: {}".format(vysledok.body,vysledok.znamka)
    return render(request,"view_test.html",{"test":test})
