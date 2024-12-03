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
from datetime import timedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


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
        user.last_name = request.POST.get('apellido')
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


# create views gestion_pedidos
@login_required
def gestion_pedidos(request):
    # Obtener los pedidos pendientes, en proceso y repartidores disponibles desde la base de datos
    pedidos_pendientes = Pedido.objects.filter(estado__nombre="Pendiente")
    pedidos_en_proceso = Pedido.objects.filter(estado__nombre="En Proceso")
    repartidores_disponibles = User.objects.filter(groups__name='Repartidor', mascampos__is_active=True)

    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        accion = request.POST.get('accion')
        pedido = Pedido.objects.get(id_pedido=pedido_id)

        if accion == 'en_proceso':
            pedido.estado = Estado.objects.get(nombre="En Proceso")
            pedido.save()
            messages.success(request, f'Pedido {pedido.id_pedido} está ahora en proceso.')

        elif accion == 'listo_para_despacho':
            repartidor = repartidores_disponibles.first()
            if repartidor:
                # Asignar pedido al repartidor
                pedido.usuario = repartidor
                pedido.estado = Estado.objects.get(nombre="En Camino")
                pedido.fecha = timezone.now()
                pedido.save()
                messages.success(request, f'Pedido {pedido.id_pedido} asignado a {repartidor.first_name} {repartidor.last_name} y está en camino.')
            else:
                # No hay repartidores disponibles, pedido sigue pendiente
                pedido.estado = Estado.objects.get(nombre="Pendiente")
                pedido.save()
                messages.warning(request, f'No hay repartidores disponibles para el pedido {pedido.id_pedido}. El pedido quedará pendiente.')

    context = {
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_en_proceso': pedidos_en_proceso,
        'repartidores': repartidores_disponibles
    }
    return render(request, 'EncargadoDeDespacho/gestion_pedidos.html', context)

def registro_pedidos_no_registrados(request):
    if request.method == 'POST':
        try:
            # Extraer los datos del cliente desde la solicitud POST
            cliente_data = json.loads(request.body)
            nombre = cliente_data.get('nombre')
            telefono = cliente_data.get('telefono')
            ubicacion = cliente_data.get('ubicacion')
            correo = cliente_data.get('correo')
            
            # Crear un nuevo cliente no registrado
            cliente_no_registrado = ClienteNoRegistrado.objects.create(
                nombre=nombre,
                telefono=telefono,
                ubicacion=ubicacion,
                correo=correo
            )

            # Extraer los datos del pedido
            platillos_data = cliente_data.get('platillos', [])
            total = 0
            subtotal = 0

            # Crear el pedido
            pedido = Pedido.objects.create(
                cliente_no_registrado=cliente_no_registrado,
                fecha=timezone.now(),
                total=0,  # El total se actualizará más adelante
                subtotal=0,  # El subtotal se actualizará más adelante
                tipo_pago='efectivo',
                total_puntos=0,
                estado=Estado.objects.get(nombre='Pendiente')
            )

            # Crear las líneas de pedido
            for platillo_data in platillos_data:
                platillo_id = platillo_data.get('id')
                cantidad = platillo_data.get('cantidad', 1)
                
                platillo = Platillo.objects.get(id_platillo=platillo_id)
                subtotal_orden = platillo.precio * cantidad
                total += subtotal_orden
                
                LineaPedidos.objects.create(
                    pedido=pedido,
                    platillo=platillo,
                    cantidad=cantidad,
                    total_orden=subtotal_orden,
                    valor_puntos=0  # No se consideran puntos para clientes no registrados
                )

            # Actualizar el total y el subtotal del pedido
            pedido.total = total
            pedido.subtotal = total
            pedido.save()

            return HttpResponse(status=201)
        except ValidationError as e:
            return HttpResponse(json.dumps({'error': str(e)}), status=400, content_type='application/json')
        except Exception as e:
            return HttpResponse(json.dumps({'error': 'Error al registrar el pedido.'}), status=500, content_type='application/json')

    # Renderizar la plantilla de registro de pedidos
    platillos = Platillo.objects.all()
    context = {
        'platillos': platillos
    }
    return render(request, 'RegistroDePedidos/registro_pedidos_no_registrados.html', context)


def registro_pedidos_no_registrados(request):
    if request.method == 'POST':
        try:
            cliente_data = json.loads(request.body)
            nombre = cliente_data.get('nombre')
            telefono = cliente_data.get('telefono')
            ubicacion = cliente_data.get('ubicacion')
            correo = cliente_data.get('correo')

            cliente_no_registrado = ClienteNoRegistrado.objects.create(
                nombre=nombre,
                telefono=telefono,
                ubicacion=ubicacion,
                correo=correo
            )

            platillos_data = cliente_data.get('platillos', [])
            total = 0
            total_puntos = 0

            pedido = Pedido.objects.create(
                cliente_no_registrado=cliente_no_registrado,
                fecha=timezone.now(),
                total=0,
                subtotal=0,
                tipo_pago='efectivo',  # Cambia a 'puntos' según sea necesario
                total_puntos=0,
                estado=Estado.objects.get(nombre='Pendiente')
            )

            for platillo_data in platillos_data:
                platillo_id = platillo_data.get('id')
                cantidad = platillo_data.get('cantidad', 1)

                platillo = Platillo.objects.get(id_platillo=platillo_id)
                subtotal_orden = platillo.precio * cantidad
                puntos_orden = platillo.precio_puntos * cantidad

                total += subtotal_orden
                total_puntos += puntos_orden

                LineaPedidos.objects.create(
                    pedido=pedido,
                    platillo=platillo,
                    cantidad=cantidad,
                    total_orden=subtotal_orden,
                    valor_puntos=puntos_orden
                )

            if cliente_data.get('usar_puntos', False):
                # Si el cliente paga con puntos, ajusta los valores
                pedido.total_puntos = total_puntos
                pedido.total = 0  # Total en efectivo será 0
            else:
                pedido.total = total

            pedido.subtotal = total
            pedido.save()

            return JsonResponse({'message': 'Pedido registrado con éxito.'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    platillos = Platillo.objects.all()
    context = {'platillos': platillos}
    return render(request, 'RegistroDePedidos/registro_pedidos_no_registrados.html', context)

#Cliente
def consultar_menu(request):
    platillos = Platillo.objects.all()
    platillos_dia = Platillo.objects.filter(platillo_dia=True)
    print(platillos_dia)
    context = {
        'platillos': platillos,
        'platillos_dia': list(platillos_dia)
    }
    return render(request, 'Cliente/consultar_menu.html', context)

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
            total = 0
            total_puntos = 0
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
                    # Verificar si el usuario desea pagar con puntos                 
                if tipo_pago == 'puntos':
                    if request.user.puntos.puntos_acumulados >= total_puntos:
                        pedido.total = 0
                        pedido.total_puntos = total_puntos
                        request.user.puntos.puntos_acumulados -= total_puntos
                        request.user.puntos.save()
                    else:
                        render_button = True
                        messages.warning(request, 'No tienes suficientes puntos para realizar la compra')  
                        return render(request, 'Cliente/registro_pedido.html', {
                            'platillos': platillos,
                            'carrito_items': carrito.items.all(),
                            'total': total,
                            'usuario': datos_usuario,
                            'render_button':render_button,
                            'total_puntos':total_puntos,
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
                    pedido.subtotal = total
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