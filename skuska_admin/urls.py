from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^auth/$', views.auth_view),
    url(r'^invalid/$',views.invalid_login),
]
