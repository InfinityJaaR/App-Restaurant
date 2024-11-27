from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group  # Agregar Group aquí
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib import messages
from django.contrib.auth import logout

# Create your views here.
@login_required
def home(request):
    user = request.user
    is_admin = user.groups.filter(name='Administrador').exists()
    is_client = user.groups.filter(name='Cliente').exists()
    is_repartidor = user.groups.filter(name='Repartidor').exists()
    is_despachador = user.groups.filter(name='Encargado de Despachos').exists()
    is_menu = user.groups.filter(name='Encargado de Menu').exists()
    is_registros = user.groups.filter(name='Registro de Pedidos').exists()
    context = {
        'user': user,
        'is_admin': is_admin,
        'is_client': is_client,
        'is_repartidor': is_repartidor,
        'is_despachador': is_despachador,
        'is_menu': is_menu,
        'is_registros': is_registros
    }
    return render(request, 'home.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def registro(request):
    if request.method == 'POST':
        nombre = request.POST['first_name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        password = request.POST['password1']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=email).exists():
                messages.error(request, 'El email ya está registrado')
            else:
                user = User.objects.create_user(username=email, email=email, password=password, first_name=nombre)
                user.save()
                user.groups.set([1])
                MasCampos.objects.create(user=user, telefono=phone, direccion=address)
                messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
                return redirect('login')
        else:
            messages.error(request, 'Las contraseñas no coinciden')
    return render(request, 'login')

@login_required
def nuevoUsuario(request):
    if request.method == 'POST':
        nombre = request.POST['first_name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password1']
        password2 = request.POST['password2']
        groups = request.POST['groups']

        if password == password2:
            if User.objects.filter(username=email).exists():
                messages.error(request, 'El email ya está registrado')
            else:
                user = User.objects.create_user(username=email, email=email, password=password, first_name=nombre)
                user.save()
                user.groups.set([groups])
                MasCampos.objects.create(user=user, telefono=phone)
                messages.success(request, 'Usuario creado exitosamente')
                return redirect('gestionarUsuario')
        else:
            messages.error(request, 'Las contraseñas no coinciden')
    
    grupos = Group.objects.exclude(id__in=[1, 2])  # Excluye grupos Cliente (1) y Administrador (2)
    return render(request, 'Administrador/nuevoUsuario.html', {'grupos': grupos})

@login_required
def gestionarUsuario(request):
    # Excluye usuarios de los grupos Cliente (1), Administrador (2) y superusuario
    usuarios = User.objects.exclude(groups__in=[1, 2]).exclude(is_superuser=True).select_related('mascampos').prefetch_related('groups')
    grupos = Group.objects.exclude(id__in=[1, 2])  # Excluye grupos Cliente y Administrador
    
    context = {
        'usuarios': usuarios,
        'grupos': grupos
    }
    return render(request, 'Administrador/gestionarUsuario.html', context)