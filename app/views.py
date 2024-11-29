from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib import messages
from django.contrib.auth import logout
from django.core.paginator import Paginator

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
def nuevoUsuario(request, id=None):
    if id:
        user = User.objects.get(id=id)
        mascampos = MasCampos.objects.get(user=user)
    else:
        user = None
        mascampos = None

    if request.method == 'POST':
        nombre = request.POST['first_name']
        email = request.POST['email']
        phone = request.POST['phone']
        carnet = request.POST['carnet']
        password = request.POST['password1']
        password2 = request.POST['password2']
        groups = request.POST['groups']

        if password == password2:
            if user:
                user.first_name = nombre
                user.email = email
                user.username = email
                if password:
                    user.set_password(password)
                user.save()
                user.groups.set([groups])
                mascampos.telefono = phone
                mascampos.carnet = carnet
                mascampos.save()
                messages.success(request, 'Usuario actualizado exitosamente')
            else:
                if User.objects.filter(username=email).exists():
                    messages.error(request, 'El email ya está registrado')
                else:
                    user = User.objects.create_user(username=email, email=email, password=password, first_name=nombre)
                    user.save()
                    user.groups.set([groups])
                    MasCampos.objects.create(user=user, telefono=phone, carnet=carnet)
                    messages.success(request, 'Usuario creado exitosamente')
            return redirect('gestionarUsuario')
        else:
            messages.error(request, 'Las contraseñas no coinciden')
    
    grupos = Group.objects.exclude(id__in=[1, 2])  # Excluye grupos Cliente (1) y Administrador (2)
    context = {
        'grupos': grupos,
        'user': user,
        'mascampos': mascampos
    }
    return render(request, 'Administrador/nuevoUsuario.html', context)

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

@login_required
def eliminarUsuario(request, id):
    try:
        if request.method == 'POST':
            user = User.objects.get(id=id)
            user.delete()
            messages.success(request, 'Usuario eliminado exitosamente')
        else:
            messages.error(request, 'Método no permitido')
    except User.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
    except Exception as e:
        messages.error(request, f'Error al eliminar usuario: {str(e)}')
    return redirect('gestionarUsuario')

# create views repartidor
# create views perfil de repartidor
@login_required
def perfil(request):
    if request.method == 'POST':
        nuevo_estado = request.POST.get('disponibilidad')
        request.user.mascampos.is_active = bool(int(nuevo_estado))
        request.user.mascampos.save()  # Save the MasCampos instance
        messages.success(request, 'Estado actualizado correctamente')
        return redirect('repartidor')

    return render(request, 'Repartidor/perfil.html', {'user': request.user})

# create views pedidos de repartidor
@login_required
def pedidos(request):
    if request.method == 'POST':
        pedido = Pedido.objects.get(id_pedido=request.POST.get('id_pedido'))
        pedido.estado = Estado.objects.get(id_estado=3)  # Cambiado a 3 para marcar como entregado
        pedido.save()
        messages.success(request, 'Pedido entregado correctamente')
        return redirect('pedidos')

    pedidos_asignados = Pedido.objects.filter(usuario=request.user)
    pedidos_entregados = pedidos_asignados.filter(estado__id_estado=3)
    
    return render(request, 'Repartidor/pedido.html', {'pedidos': pedidos_asignados, 'pedidos_entregados': pedidos_entregados})
    
# create views detalle de pedido
@login_required
def detalle_pedido(request, id_pedido):
    pedido = Pedido.objects.get(id_pedido=id_pedido)
    
    if request.method == 'POST':
        pedido.estado = Estado.objects.get(id_estado=3)  # 3 = Entregado
        pedido.save()
        messages.success(request, 'Pedido entregado correctamente')
        return redirect('pedidos')
        
    return render(request, 'Repartidor/detalle_pedido.html', {'pedido': pedido})

@login_required
def perfil_cliente(request):
    user = request.user
    mas_campos = MasCampos.objects.get(user=user)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('nombre')
        user.email = request.POST.get('email')
        mas_campos.direccion = request.POST.get('direccion')
        mas_campos.telefono = request.POST.get('telefono')
        
        user.save()
        mas_campos.save()
        messages.success(request, 'Perfil actualizado exitosamente')
        return redirect('perfil_cliente')
        
    context = {
        'user': user,
        'mas_campos': mas_campos
    }
    return render(request, 'Cliente/perfil.html', context)






