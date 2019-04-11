from django.conf.urls import url
from . import views


urlpatterns = [
    url('^analysis/$', views.AnalysisView.as_view()),
    url('^optimization/$', views.OptimizationView.as_view()),
    url('^analysis/api/$', views.AnalysisApi.as_view()),
    url('^optimization/api/$', views.OptimizationApi.as_view()),
    url('^mapping/$', views.GetMappingView.as_view())
]


