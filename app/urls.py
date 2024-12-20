from django.urls import path
from .views import *
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('desactivar_puntos/', desactivar_puntos, name='desactivar_puntos'),
    path('reactivar_puntos/', reactivar_puntos, name='reactivar_puntos'),
    path('desactivar_cupones/', desactivar_cupones, name='desactivar_cupones'),
    path('reactivar_cupones/', reactivar_cupones, name='reactivar_cupones'),
    path('crear_cupon/', crear_cupon, name='crear_cupon'),
    path('eliminar_cupon/<int:id_cupon>/', eliminar_cupon, name='eliminar_cupon'),
    path('editar_cupon/', editar_cupon, name='editar_cupon'),
    path('gestionar_regalias/', gestionar_regalias, name='gestionar_regalias'),
    path('consultar_menu/', consultar_menu, name='consultar_menu'),
    path('consultar_menu_dia/', consultar_menu_dia, name='consultar_menu_dia'),
    path('carrito/', ver_carrito, name='ver_carrito'),
    path('agregar/<int:platillo_id>/', agregar_carrito, name='agregar_carrito'),
    path('realiza_pedido/', realizar_pedido, name='procesar_pago'),
    path('vaciar_carrito/', vaciar_carrito, name='vaciar_carrito'),
    path('quitar_unidad/<int:platillo_id>/', quitar_unidad_carrito, name='quitar_unidad_carrito'),
    path('eliminar/<int:platillo_id>/', eliminar_del_carrito, name='eliminar_del_carrito'),
    path('procesar_pago', registro_pedido_cliente, name='registro_pedido_cliente'),
    path('consultar_pedidos/', ver_pedidos, name='consultar_pedidos'),
    path('consultar_pedido/<int:pedido_id>/', consultar_pedido, name='consultar_pedido'),
    path('pedido/<int:pedido_id>/reclamo/', registrar_reclamo, name='registrar_reclamo'),
    path('gestion_platillos/', gestionar_platillos, name='gestion_platillos'),
    path('gestion_platillos/agregar/', agregar_platillo, name='agregar_platillo'),
    path('gestion_platillos/editar/<int:platillo_id>/', editar_platillo, name='editar_platillo'),
    path('gestion_platillos/eliminar/<int:platillo_id>/', eliminar_platillo, name='eliminar_platillo'),
    path('menu_dia/', menu_diario, name='menu_diario'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)