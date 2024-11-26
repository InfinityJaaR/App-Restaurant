from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('registro/', registro, name='registro'),
    path('repartidor/', perfil, name='repartidor'),

]