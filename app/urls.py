from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('logout/', logout_view, name='logout'),
    path('registro/', registro, name='registro'),
    path('nuevoUsuario/', nuevoUsuario, name='nuevoUsuario'),
    path('usuarios/editarUsuario/<int:id>/', nuevoUsuario, name='editarUsuario'),
    path('usuarios', gestionarUsuario, name='gestionarUsuario'),
    path('repartidor/', perfil, name='repartidor'),
    path('pedidos/', pedidos, name='pedidos'),
    path('pedidos/<int:id_pedido>/', detalle_pedido, name='detalle_pedido'),
    path('usuarios/eliminar/<int:id>/', eliminarUsuario, name='eliminarUsuario'),
    path('preparar_pedidos/', preparar_pedidos, name='preparar_pedidos'),
    path('detalles_pedido/<int:pedido_id>/', detalles_pedido, name='detalles_pedido'),
    path('asignar_pedidos/', asignar_pedidos, name='asignar_pedidos'),
    path('registro_pedidos_no_registrados/', registro_pedidos_no_registrados, name='registro_pedidos_no_registrados'),
    path('perfil-cliente/', perfil_cliente, name='perfil_cliente'),
]