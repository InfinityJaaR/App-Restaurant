from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('logout/', logout_view, name='logout'),
    path('registro/', registro, name='registro'),
    path('repartidor/', perfil, name='repartidor'),
    path('pedidos/', pedidos, name='pedidos'),
    path('pedidos/<int:id_pedido>/', detalle_pedido, name='detalle_pedido'),

]