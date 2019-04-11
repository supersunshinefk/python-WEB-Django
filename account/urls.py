from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^account/$', views.AccountView.as_view()),
    url(r'^account/api/$', views.AccountApi.as_view()),
]

