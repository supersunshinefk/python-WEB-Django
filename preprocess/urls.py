from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^filter/$', views.FilterView.as_view()),
    url(r'^filter/api/$', views.FilterApi.as_view()),
    url(r'^organizer/$', views.OrganizerView.as_view()),
    url(r'^organizer/api/$', views.OrganizerApi.as_view()),
]
