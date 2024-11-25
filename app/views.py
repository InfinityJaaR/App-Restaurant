from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import *

# Create your views here.
@login_required
def index(request):
    return render(request, 'home.html')

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
                return HttpResponse('El email ya está registrado')
            else:
                user = User.objects.create_user(username=email, email=email, password=password, first_name=nombre)
                user.save()
                user.groups.set([1])
                MasCampos.objects.create(user=user, telefono=phone, direccion=address)
                return redirect('login')
        else:
            return HttpResponse('Las contraseñas no coinciden')
        
        
def registrar_pedido(request):
    if request.method == "POST":
        # Crear DetallesCliente
        nombre_cliente = request.POST.get("nombre_cliente")
        telefono_cliente = request.POST.get("telefono_cliente")
        direccion_cliente = request.POST.get("direccion_cliente")

        detalles_cliente = DetallesCliente.objects.create(
            nombre=nombre_cliente,
            telefono=telefono_cliente,
            direccion=direccion_cliente
        )

        # Crear Pedido
        tipo_pago = request.POST.get("tipo_pago")
        platillos = request.POST.getlist("platillo[]")
        cantidades = request.POST.getlist("cantidad[]")
        estado_inicial = Estado.objects.get(nombre="En proceso")

        pedido = Pedido.objects.create(
            usuario=request.user,  # Encargado registrado
            detalles_cliente=detalles_cliente,
            fecha=now(),
            total=0,
            subtotal=0,
            tipo_pago=tipo_pago,
            total_puntos=0,
            estado=estado_inicial,
        )

        # Crear las líneas del pedido
        subtotal = 0
        for platillo_id, cantidad in zip(platillos, cantidades):
            platillo = Platillo.objects.get(id=platillo_id)
            cantidad = int(cantidad)
            total_orden = platillo.precio * cantidad

            LineaPedidos.objects.create(
                pedido=pedido,
                platillo=platillo,
                cantidad=cantidad,
                total_orden=total_orden,
                valor_puntos=0,
            )

            subtotal += total_orden

        # Actualizar totales
        pedido.subtotal = subtotal
        pedido.total = subtotal
        pedido.save()

        return redirect("vista_pedidos")

    else:
        platillos = Platillo.objects.all()
        return render(request, "registroPedidosEmpleado.html", {
            "platillos": platillos,
        })