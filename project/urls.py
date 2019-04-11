from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.ProjectView.as_view()),
    url('^startapi/$', views.ProjectStartApiView.as_view())

]
