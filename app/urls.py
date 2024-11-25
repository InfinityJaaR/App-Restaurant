from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', index, name='index'),
    path('registro/', registro, name='registro'),
    path('registrar_pedido/', views.registrar_pedido, name='registrar_pedido'),
    path('encargado_despacho/', views.encargado_despacho, name='encargado_despacho'),
    path('marcar_en_preparacion/<int:pedido_id>/', views.marcar_en_preparacion, name='marcar_en_preparacion'),
    path('marcar_listo_para_envio/<int:pedido_id>/', views.marcar_listo_para_envio, name='marcar_listo_para_envio'),
]