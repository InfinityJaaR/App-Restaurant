from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', index, name='index'),
    path('registro/', registro, name='registro'),
    path('registrar_pedido/', views.registrar_pedido, name='registrar_pedido'),
]