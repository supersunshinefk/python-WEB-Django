from django.conf.urls import url
from . import views


urlpatterns = [
    url('login/', views.LoginView.as_view()),
    url('register', views.RegisterView.as_view()),
    url('logout/', views.LogoutView.as_view()),
    url('info/', views.UserInfoView.as_view()),

]

