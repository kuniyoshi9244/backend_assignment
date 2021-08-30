from django.urls import path
from . import views

urlpatterns = [
    path('', views.AccountRegistration.as_view(), name='registeration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('home/',views.HomeView.as_view(), name="home"),
]