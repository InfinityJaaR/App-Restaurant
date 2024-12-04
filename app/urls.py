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
    path('gestion_pedidos/', gestion_pedidos, name='gestion_pedidos'),
    path('registro_pedidos_no_registrados/', registro_pedidos_no_registrados, name='registro_pedidos_no_registrados'),
    path('perfil-cliente/', perfil_cliente, name='perfil_cliente'),
    path('desactivar_puntos/', desactivar_puntos, name='desactivar_puntos'),
    path('reactivar_puntos/', reactivar_puntos, name='reactivar_puntos'),
    path('desactivar_cupones/', desactivar_cupones, name='desactivar_cupones'),
    path('reactivar_cupones/', reactivar_cupones, name='reactivar_cupones'),
    path('crear_cupon/', crear_cupon, name='crear_cupon'),
    path('gestionar_regalias/', gestionar_regalias, name='gestionar_regalias'),
]