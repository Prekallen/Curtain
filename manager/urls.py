from django.urls import path
from . import views

urlpatterns = [
    path('', views.manager),
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout_view),
]