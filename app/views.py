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
from django.urls import path
from .models import Cupon, Puntos, MasCampos
import json

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