from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^auth/$', views.auth_view),
    url(r'^invalid/$',views.invalid_login),
    url(r'^manage/$',views.manage),
    url(r'^view_results/$',views.view_results),
    url(r'^set/$',views.set_tests),
    url(r'^view_test/$',views.view_test),
    url(r'^find_test/$',views.find_test),
    url(r'^find_results/$',views.find_results)
]
