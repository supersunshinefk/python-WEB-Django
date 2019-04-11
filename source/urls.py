from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^data_source/$', views.SourceView.as_view()),
    url(r'^data_pipe/$', views.PipeView.as_view()),
    url(r'^data_source/api/$', views.SourceApi.as_view()),
    url(r'^data_pipe/api/$', views.PipeApi.as_view()),
]

