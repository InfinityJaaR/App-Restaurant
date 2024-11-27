from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib import messages

# Create your views here.
@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_exempt
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
        pedido.estado = Estado.objects.get(id_estado=1)  # Cambiado a 1 para marcar como entregado
        pedido.save()
        messages.success(request, 'Pedido entregado correctamente')
        return redirect('pedidos')

    pedidos_asignados = Pedido.objects.filter(usuario=request.user)
    return render(request, 'Repartidor/pedido.html', {'pedidos': pedidos_asignados})
# create views detalle de pedido
@login_required
def detalle_pedido(request, id_pedido):
    pedido = Pedido.objects.get(id_pedido=id_pedido)
    
    if request.method == 'POST':
        pedido.estado = Estado.objects.get(id_estado=3)  # 1 = Entregado
        pedido.save()
        messages.success(request, 'Pedido entregado correctamente')
        return redirect('pedidos')
        
    return render(request, 'Repartidor/detalle_pedido.html', {'pedido': pedido})