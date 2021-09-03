from django.urls import path
from django.contrib.auth import views as av
from . import views

urlpatterns = [
    path('', views.AccountRegistration.as_view(), name='registeration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', av.LogoutView.as_view(), name='logout'),
    path('home/',views.HomeView.as_view(), name="home"),
]