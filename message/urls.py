from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^message/$', views.MessageView.as_view()),
    url(r'^message/api/$', views.MessageApi.as_view()),
]


