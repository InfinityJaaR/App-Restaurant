from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib import messages
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
import json
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.views.decorators.cache import never_cache

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
                Puntos.objects.create(user=user)
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
        pedido.estado = Estado.objects.get(id_estado=6)  # Cambiado a 3 para marcar como entregado
        pedido.save()
        messages.success(request, 'Pedido entregado correctamente')
        return redirect('pedidos')

    pedidos_asignados = Pedido.objects.filter(repartidor=request.user)
    pedidos_entregados = pedidos_asignados.filter(estado__id_estado=6)# estado 3 = Entregados
    
    return render(request, 'Repartidor/pedido.html', {'pedidos': pedidos_asignados, 'pedidos_entregados': pedidos_entregados})
    
# create views detalle de pedido
@login_required
def detalle_pedido(request, id_pedido):
    pedido = Pedido.objects.get(id_pedido=id_pedido)
    
    if request.method == 'POST':
        pedido.estado = Estado.objects.get(id_estado=6)  # 3 = Entregado
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
        user.username = request.POST.get('email')
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

# Vista para preparar pedidos
@login_required
def preparar_pedidos(request):
    if request.method == "POST":
        # Procesar el formulario enviado por el método POST
        pedido_id = request.POST.get("pedido_id")
        if not pedido_id:
            return JsonResponse({"success": False, "message": "ID de pedido no proporcionado."}, status=400)

        pedido = get_object_or_404(Pedido, id_pedido=pedido_id)

        # Verificar que el estado "Pendiente" exista
        estado_pendiente = Estado.objects.filter(nombre="Pendiente").first()
        if not estado_pendiente:
            return JsonResponse({"success": False, "message": "Estado 'Pendiente' no encontrado."}, status=404)

        # Actualizar el estado del pedido
        pedido.estado = estado_pendiente
        pedido.save()

        return JsonResponse({"success": True, "message": f"Pedido {pedido_id} ahora está en estado Pendiente."}, status=200)

    # Mostrar la tabla con la paginación
    pedidos_preparando = Pedido.objects.filter(estado__nombre="Preparando")
    paginator = Paginator(pedidos_preparando, 6)  # Mostrar 6 pedidos por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "EncargadoDeDespacho/preparar_pedidos.html", {"page_obj": page_obj})

# Vista para obtener detalles del pedido (JSON para el frontend)
@login_required
def detalles_pedido(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id_pedido=pedido_id)
        lineas = pedido.lineas.all()
        context = {
            "pedido": pedido,
            "lineas": lineas,
        }
        return render(request, "EncargadoDeDespacho/detalles_pedido.html", context)
    except Pedido.DoesNotExist:
        messages.error(request, "Pedido no encontrado")
        return redirect("preparar_pedidos")

@login_required
def asignar_pedidos(request):
    pedidos_pendientes = Pedido.objects.filter(estado__nombre="Pendiente")
    repartidores_disponibles = User.objects.filter(
        groups__name="Repartidor", mascampos__is_active=True
    )

    # Paginación para pedidos pendientes
    pedidos_paginator = Paginator(pedidos_pendientes, 3)  # Mostrar 3 pedidos por página
    pedidos_page_number = request.GET.get('pedidos_page')
    pedidos_page_obj = pedidos_paginator.get_page(pedidos_page_number)

    if request.method == "POST":
        pedido_id = request.POST.get("pedido_id")
        pedido = Pedido.objects.get(id_pedido=pedido_id)
        repartidor = repartidores_disponibles.first()

        if repartidor:
            pedido.repartidor = repartidor
            pedido.estado = Estado.objects.get(nombre="En Camino")
            repartidor.mascampos.is_active = False
            repartidor.mascampos.save()
            pedido.save()
            messages.success(request, f"Pedido {pedido_id} asignado a {repartidor.first_name}.")
        else:
            messages.warning(request, f"No hay repartidores disponibles para el pedido {pedido_id}.")

        return redirect("asignar_pedidos")

    context = {
        "pedidos_page_obj": pedidos_page_obj,
        "repartidores_disponibles": repartidores_disponibles,
    }
    return render(request, "EncargadoDeDespacho/asignar_pedidos.html", context)

# Crear vista para el encargado de pedidos
@login_required
@csrf_exempt
def registro_pedidos_no_registrados(request):
    if request.method == 'POST':
        try:
            # Extraer los datos del cliente desde la solicitud POST
            data = json.loads(request.body)
            nombre = data.get('nombre')
            telefono = data.get('telefono')
            ubicacion = data.get('ubicacion')
            correo = data.get('correo')
            tipo_pago = data.get('tipo_pago')
            platillos_data = data.get('platillos', [])

            if not platillos_data:
                return JsonResponse({'error': 'No se han seleccionado platillos'}, status=400)

            # Crear un cliente no registrado
            cliente_no_registrado = ClienteNoRegistrado.objects.create(
                nombre=nombre,
                telefono=telefono,
                ubicacion=ubicacion,
                correo=correo
            )

            # Crear el pedido
            subtotal = 0
            pedido = Pedido.objects.create(
                cliente_no_registrado=cliente_no_registrado,
                fecha=timezone.now(),
                subtotal=0,
                total=0,
                tipo_pago=tipo_pago,
                total_puntos=0,
                estado=Estado.objects.get(nombre='Preparando')
            )

            # Crear líneas de pedido y actualizar disponibilidad
            for item in platillos_data:
                platillo_id = item.get('id')
                cantidad = int(item.get('cantidad', 1))
                platillo = Platillo.objects.get(id_platillo=platillo_id)

                if cantidad > platillo.cantidad_maxima:
                    return JsonResponse({'error': f'No hay suficiente disponibilidad para el platillo {platillo.nombre}. Disponible: {platillo.cantidad_maxima}'}, status=400)

                # Actualizar cantidad máxima
                platillo.cantidad_maxima -= cantidad
                platillo.save()

                # Calcular subtotal
                subtotal_orden = platillo.precio * cantidad
                subtotal += subtotal_orden

                # Crear línea de pedido
                LineaPedidos.objects.create(
                    pedido=pedido,
                    platillo=platillo,
                    cantidad=cantidad,
                    total_orden=subtotal_orden,
                    valor_puntos=0
                )

            # Actualizar subtotal y total del pedido
            pedido.subtotal = subtotal
            pedido.total = subtotal
            pedido.save()

            return JsonResponse({'message': 'Pedido registrado exitosamente', 'pedido_id': pedido.id_pedido}, status=201)

        except Platillo.DoesNotExist:
            return JsonResponse({'error': 'Platillo no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'Error al registrar el pedido', 'details': str(e)}, status=500)

    # Renderizar la plantilla con los platillos del día
    platillos = Platillo.objects.filter(platillo_dia=True)
    context = {
        'platillos': platillos
    }
    return render(request, 'RegistroDePedidos/registro_pedidos_no_registrados.html', context)

# Views

def desactivar_puntos(request):
    if request.method == 'POST':
        Puntos.objects.update(disponibilidad=False)
        messages.success(request, 'Todos los puntos han sido desactivados correctamente.')
        return redirect('gestionar_regalias')

def reactivar_puntos(request):
    if request.method == 'POST':
        Puntos.objects.filter(fecha_caducidad__gte=timezone.now()).update(disponibilidad=True)
        messages.success(request, 'Puntos válidos han sido reactivados correctamente.')
        return redirect('gestionar_regalias')

def desactivar_cupones(request):
    if request.method == 'POST':
        Cupon.objects.update(disponibilidad=False)
        messages.success(request, 'Todos los cupones han sido desactivados correctamente.')
        return redirect('gestionar_regalias')

def reactivar_cupones(request):
    if request.method == 'POST':
        Cupon.objects.filter(fecha_expiracion__gte=timezone.now()).update(disponibilidad=True)
        messages.success(request, 'Cupones válidos han sido reactivados correctamente.')
        return redirect('gestionar_regalias')

def crear_cupon(request):
    if request.method == 'POST':
        codigo = request.POST['codigo']
        descuento = request.POST['descuento']
        fecha_expiracion = request.POST['fecha_expiracion']
        
        # Validar que la fecha no sea menor a hoy
        if fecha_expiracion < str(timezone.now().date()):
            messages.error(request, 'La fecha de expiración no puede ser menor a la de hoy.')
            return redirect('gestionar_regalias')

        Cupon.objects.create(
            codigo=codigo,
            descuento=descuento,
            fecha_expiracion=fecha_expiracion,
            disponibilidad=True
        )
        messages.success(request, 'Cupón creado exitosamente.')
        return redirect('gestionar_regalias')

def gestionar_regalias(request):
    cupones_list = Cupon.objects.all()
    query = request.GET.get('q')
    if query:
        cupones_list = cupones_list.filter(codigo__icontains=query)

    paginator = Paginator(cupones_list, 4)  # Máximo de 4 cupones por página
    page_number = request.GET.get('page')
    cupones = paginator.get_page(page_number)

    return render(request, 'Administrador/gestionarRegalias.html', {'cupones': cupones})

#Cliente
def consultar_menu(request):
    carrito = obtener_carrito(request)
    items = carrito.items.all()
    total = sum(item.total for item in items)
    platillos = Platillo.objects.all()
    platillos_dia = Platillo.objects.filter(platillo_dia=True)    
    context = {
        'platillos': platillos,
        'platillos_dia': list(platillos_dia),
        'total':total
    }
    return render(request, 'Cliente/consultar_menu.html', context)

@login_required
def consultar_menu_dia(request):
    carrito = obtener_carrito(request)
    items = carrito.items.all()
    total = sum(item.total for item in items)
    platillos_dia = Platillo.objects.filter(platillo_dia=True)
    context = {
        'platillos_dia': platillos_dia,
        'total':total
    }
    return render(request, 'Cliente/consultar_menu_dia.html', context)

def obtener_carrito(request):
    """Obtiene el carrito del usuario si está autenticado o crea uno temporal para no autenticados."""
    carrito = None  # Inicializamos la variable carrito antes de entrar al bloque condicional.
    
    if request.user.is_authenticated:
        # Si el usuario está autenticado, obtenemos o creamos un carrito con su usuario
           carrito, created = Carrito.objects.get_or_create(usuario=request.user)

    else:
        # Si el usuario no está autenticado, usamos la session_key
        session_key = request.session.session_key
        if not session_key:
            # Si no existe un session_key, lo creamos
            request.session.create()
            session_key = request.session.session_key
        
        # Creamos un carrito con session_id
        carrito, created = Carrito.objects.get_or_create(session_id=session_key, usuario=None)
    return carrito


def agregar_carrito(request, platillo_id):
    """Agregar un platillo al carrito con su cantidad y actualizar el total"""
    carrito = obtener_carrito(request)
    platillo = get_object_or_404(Platillo, id_platillo=platillo_id)
    cantidad = int(request.POST.get('cantidad', 1))
    
    # Verificar si el platillo ya está en el carrito
    item, created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        platillo=platillo,
        defaults={'cantidad': 0, 'precio_unitario': platillo.precio, 'total': 0}
    )

    # Actualizar la cantidad y el total del platillo
    item.cantidad += cantidad
    item.actualizar_total()

    return redirect('ver_carrito')
@never_cache
def ver_carrito(request):
    """Mostrar los items en el carrito del usuario"""
    carrito = obtener_carrito(request)
    items = carrito.items.all()

    # Imprimir el id del platillo de cada item en el carrito
    for item in items:
        print(f"Platillo: {item.platillo.nombre}, ID del platillo: {item.platillo.id_platillo}")

    # Calcular el total del carrito
    total = sum(item.total for item in items)

    # Pasar los items y el total a la plantilla
    return render(request, 'Cliente/mostrar_carrito.html', {
        'carrito_items': items, 
        'total_carrito': total
    })


@login_required
def realizar_pedido(request):
    carrito = obtener_carrito(request)
    items = carrito.items.all()

    if not items:
        return redirect('ver_carrito')  # Si el carrito está vacío, redirige al carrito

    # Crear el pedido
    pedido = Pedido.objects.create(
        usuario=request.user,
        fecha=timezone.now(),
        total=0,
        subtotal=0,
        tipo_pago='efectivo',  # O toma del formulario de pago
        total_puntos=0,  # Agregar lógica de puntos aquí
        estado_id=1  # Estado en proceso
    )

    # Crear líneas de pedido y actualizar el total del pedido
    for item in items:
        LineaPedidos.objects.create(
            pedido=pedido,
            platillo=item.platillo,
            cantidad=item.cantidad,
            total_orden=item.total,
            valor_puntos=item.platillo.precio_puntos
        )
        pedido.total += item.total
        pedido.subtotal += item.total

    pedido.save()

    # Limpiar el carrito después de crear el pedido
    carrito.items.all().delete()

    return redirect('ver_pedido', pedido_id=pedido.id_pedido)

def quitar_unidad_carrito(request, platillo_id):
    """Eliminar una unidad de un platillo del carrito"""
    carrito = obtener_carrito(request)
    item = get_object_or_404(ItemCarrito, carrito=carrito, platillo__id_platillo=platillo_id)

    # Si la cantidad es mayor a 1, reducimos la cantidad
    if item.cantidad > 1:
        item.cantidad -= 1
        item.actualizar_total()  # Recalcular el total del item
    else:
        # Si la cantidad es 1, eliminamos el item del carrito
        item.delete()

    return redirect('ver_carrito')

def eliminar_del_carrito(request, platillo_id):
    """Eliminar un platillo completo del carrito"""
    carrito = obtener_carrito(request)
    item = get_object_or_404(ItemCarrito, carrito=carrito, platillo__id_platillo=platillo_id)
    item.delete()  # Eliminar el item del carrito
    return redirect('ver_carrito')

def vaciar_carrito(request):
    """Vaciar todo el carrito"""
    carrito = obtener_carrito(request)
    carrito.items.all().delete()  # Eliminar todos los items del carrito
    return redirect('ver_carrito')

@never_cache
@login_required(login_url='/accounts/login/') 
def registro_pedido_cliente(request):

        # Mostrar los platillos disponibles y el carrito
    platillos = Platillo.objects.all()
    carrito = obtener_carrito(request) 
    items = carrito.items.all()
    total_puntos = 0
    total = sum(item.total for item in items)
    for item in items:
        platillo = item.platillo
        cantidad = item.cantidad
        total_puntos += platillo.precio_puntos * cantidad
        print(total_puntos)

    usuario= request.user
    mas_campos = usuario.mascampos
    datos_usuario = {
        'nombre': usuario.get_full_name(),
        'correo': usuario.email,
        'telefono': mas_campos.telefono,
        'direccion': mas_campos.direccion,
        }

    if request.method == 'POST':
        try:
            # Datos de los platillos del carrito (se pueden obtener del carrito del usuario)
            carrito = obtener_carrito(request)  # Suponiendo que ya tienes la función obtener_carrito para obtener el carrito del usuario
            items = carrito.items.all()
            
            tipo_pago=request.POST.get('tipo_pago')
            cuponAux=request.POST.get('cupon')
            total = 0
            total_puntos = 0
            subtotal=0            
            recompensa_puntos = 0  # Inicializamos la variable aquí
            carrito = obtener_carrito(request) 
            items = carrito.items.all()
            puntos_usuario = Puntos.objects.filter(user=request.user).first()

            if tipo_pago =="no_pago":
                     total = sum(item.total for item in items)
                     for item in items:
                         platillo = item.platillo
                         cantidad = item.cantidad
                         total_puntos += platillo.precio_puntos * cantidad
                         print(total_puntos)
                         render_button = True
                         messages.warning(request, 'Seleccione un metodo de pago')  
                         return render(request, 'Cliente/registro_pedido.html', {
                            'platillos': platillos,
                            'carrito_items': carrito.items.all(),
                            'total': total,
                            'usuario': datos_usuario,
                            'render_button':render_button,
                            'total_puntos':total_puntos,
                            })

            if items != 0:
                pedido = Pedido.objects.create(
                usuario=request.user,  # El usuario autenticado
                fecha=timezone.now(),
                total=0,
                subtotal=0,
                tipo_pago=request.POST.get('tipo_pago', 'efectivo'),  # Obtenemos el tipo de pago del formulario (efectivo o tarjeta)
                total_puntos=0,
                estado=Estado.objects.get(nombre='Pendiente'))
                
                # Crear las lineas del pedido
                for item in items:
                    platillo = item.platillo
                    cantidad = item.cantidad
                    subtotal_orden = platillo.precio * cantidad
                    puntos_orden = platillo.precio_puntos * cantidad
                    # Sumar la recompensa por cada platillo
                    recompensa_puntos += platillo.recompensa_puntos * cantidad
                    total += subtotal_orden
                    total_puntos += puntos_orden
                    
                    LineaPedidos.objects.create(
                        pedido=pedido,
                        platillo=platillo,
                        cantidad=cantidad,
                        total_orden=subtotal_orden,
                        valor_puntos=puntos_orden
                    )
                    
                    subtotal = total                            
                    if cuponAux!="":                        
                        try:         
                            print(cuponAux)
                            cupon = Cupon.objects.get(codigo=cuponAux)
                            print(cupon)                    
                            if cupon.disponibilidad and cupon.fecha_expiracion >= timezone.now().date():
                                subtotal = total
                                total = cupon.aplicar_descuento(total)   
                                cupon.disponibilidad = False
                                cupon.save()                                         
                            else:                        
                                total = sum(item.total for item in items)
                                for item in items:
                                    platillo = item.platillo
                                    cantidad = item.cantidad
                                    total_puntos += platillo.precio_puntos * cantidad                            
                                render_button = True
                                messages.error(request, "El cupón no es válido o ha caducado.")                        
                                return render(request, 'Cliente/registro_pedido.html', {
                                    'platillos': platillos,
                                    'carrito_items': carrito.items.all(),
                                    'total': total,
                                    'usuario': datos_usuario,
                                    'render_button':render_button,
                                    'total_puntos':total_puntos,
                                    })                        
                        except Cupon.DoesNotExist as e:                                                   
                            total = sum(item.total for item in items)
                            for item in items:
                                platillo = item.platillo
                                cantidad = item.cantidad
                                total_puntos += platillo.precio_puntos * cantidad                            
                                render_button = True
                                messages.error(request, "El cupón no existe.")                        
                                return render(request, 'Cliente/registro_pedido.html', {
                                    'platillos': platillos,
                                    'carrito_items': carrito.items.all(),
                                    'total': total,
                                    'usuario': datos_usuario,
                                    'render_button':render_button,
                                    'total_puntos':total_puntos,
                                    })                    
                    
                # Verificar si el usuario desea pagar con puntos                 
                if tipo_pago == 'puntos':
                    puntos_usuario = request.user.puntos  
                    if puntos_usuario.son_validos():  
                        if puntos_usuario.puntos_acumulados >= total_puntos:
                               pedido.total = 0
                               pedido.total_puntos = total_puntos
                               puntos_usuario.puntos_acumulados -= total_puntos
                               puntos_usuario.save()
                               pedido.total = total  
                               pedido.subtotal = total
                               pedido.save()                                                
                               messages.success(request, 'Registro exitoso. Pedido ID: #'+ str(pedido.id_pedido))  
                               render_button=False         
                               form_render=False   
                               carrito = obtener_carrito(request) 
                               carrito.items.all().delete()            
                               return render (request,'Cliente/registro_pedido.html',{'render_button':render_button,'form_render':form_render})                                    
                        else:
                            render_button = True
                            messages.warning(request, 'No tienes suficientes puntos para realizar la compra')
                            return render(request, 'Cliente/registro_pedido.html', {
                                    'platillos': platillos,
                                    'carrito_items': carrito.items.all(),
                                    'total': total,
                                    'usuario': datos_usuario,
                                    'render_button': render_button,
                                    'total_puntos': total_puntos,
                                    })
                    else:
                         render_button = True
                         messages.warning(request, 'Tus puntos han caducado o no están disponibles.')
                         return render(request, 'Cliente/registro_pedido.html', {
                              'platillos': platillos,
                              'carrito_items': carrito.items.all(),
                              'total': total,
                              'usuario': datos_usuario,
                              'render_button': render_button,
                              'total_puntos': total_puntos,
                              })
                else:                    
                    if puntos_usuario:                 
                        puntos_usuario.puntos_acumulados += recompensa_puntos
                    else:
                        puntos_usuario = Puntos.objects.create(
                        user=request.user,
                        puntos_acumulados=recompensa_puntos,
                        fecha_caducidad=(timezone.now() + timedelta(days=30)).date()
                        )
                           
                    pedido.total = total  # Si paga en efectivo o con tarjeta, total es el total calculado
                    pedido.subtotal = subtotal
                    pedido.save()                                                
                    puntos_usuario.save()                                    
                    
                    messages.success(request, 'Registro exitoso. Pedido ID: #'+ str(pedido.id_pedido))  
                    render_button=False         
                    form_render=False   
                    carrito = obtener_carrito(request) 
                    carrito.items.all().delete()            
                    return render (request,'Cliente/registro_pedido.html',{'render_button':render_button,'form_render':form_render})                                    
            else:
                  
                  return render(request, 'Cliente/registro_pedido.html', {
                     'platillos': platillos,
                     'carrito_items': carrito.items.all(),
                     'total': total,
                     'usuario': datos_usuario,
                     'render_button':render_button,
                     'total_puntos':total_puntos,
                     })
                 
        except Exception as e:                        
            return JsonResponse({'error': str(e)}, status=500)
    
    if len(items) > 0:
        render_button = True
    else:
        render_button = False

    return render(request, 'Cliente/registro_pedido.html', {
        'platillos': platillos,
        'carrito_items': carrito.items.all(),
        'total': total,
        'usuario': datos_usuario,
        'render_button':render_button,
        'total_puntos':total_puntos,
    })

@login_required
def gestionar_platillos(request):
    platillos = Platillo.objects.all()
    context = {
        'platillos': platillos
    }
    return render(request, 'CatalogoYMenu/catalogo.html', context)

@login_required
def menu_diario(request):
    platillos = Platillo.objects.all()
    context = {
        'platillos': platillos
    }
    return render(request, 'CatalogoYMenu/menudia.html', context)