from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.metadata),
    url(r'^test/$',views.test),
    url(r'^vysledok/$',views.vysledok),
]
