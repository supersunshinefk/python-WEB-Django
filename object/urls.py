from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^objectgroup/$', views.ObjectGroupView.as_view()),
    url(r'^objectgroup/api/$', views.GroupApi.as_view()),
    url(r'^object/api/$', views.ObjectApi.as_view()),
    url(r'^object/$', views.ObjectsView.as_view()),
    url(r'^apiq/$', views.ApiqGetView.as_view()),
    url(r'^object_info/$', views.ObjectInfo.as_view())
]
