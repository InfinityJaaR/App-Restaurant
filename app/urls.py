from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('logout/', logout_view, name='logout'),
    path('registro/', registro, name='registro'),
    path('usuarios/nuevoUsuario/', nuevoUsuario, name='nuevoUsuario'),
    path('usuarios', gestionarUsuario, name='gestionarUsuario'),
]