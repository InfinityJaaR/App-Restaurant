from django.db import models
from django.contrib.auth.models import User 
from django.core.validators import MinValueValidator, MaxValueValidator

class MasCampos(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    carnet = models.CharField(max_length=8, default='00000000')
    telefono = models.CharField(max_length=9, default='000000000')
    direccion = models.CharField(max_length=255, default='Sin dirección', blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Puntos(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="puntos")
    puntos_acumulados = models.IntegerField(default=0)
    fecha_caducidad = models.DateField()
    disponibilidad = models.BooleanField(default=True)

    def __str__(self):
        return f"Puntos de {self.user.username}"


class Estado(models.Model):
    id_estado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=256)

    def __str__(self):
        return self.nombre


class Platillo(models.Model):
    id_platillo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=256)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to="platillos/")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_puntos = models.IntegerField()
    recompensa_puntos = models.IntegerField()
    platillo_dia = models.BooleanField(default=False)
    cantidad_maxima = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    TIPO_PAGO_CHOICES = [
        ("efectivo", "Efectivo"),
        ("tarjeta", "Tarjeta"),
    ]
    
    id_pedido = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pedidos", null=True, blank=True, default=None)
    cliente_no_registrado = models.ForeignKey('ClienteNoRegistrado', on_delete=models.CASCADE, related_name="pedidos", null=True, blank=True, default=None)
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_pago = models.CharField(
        max_length=256,
        choices=TIPO_PAGO_CHOICES,
        default="efectivo"  # Valor predeterminado
    )
    total_puntos = models.IntegerField()
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name="pedidos")

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.usuario and not self.cliente_no_registrado:
            raise ValidationError('Debe existir un usuario registrado o un cliente no registrado.')
        if self.usuario and self.cliente_no_registrado:
            raise ValidationError('No se puede asignar un usuario y un cliente no registrado al mismo tiempo.')

    def __str__(self):
        return f"Pedido {self.id_pedido} de {self.usuario or self.cliente_no_registrado}"



class LineaPedidos(models.Model):
    id_linea_pedido = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="lineas")
    platillo = models.ForeignKey(Platillo, on_delete=models.CASCADE, related_name="lineas")
    cantidad = models.IntegerField()
    total_orden = models.DecimalField(max_digits=10, decimal_places=2)
    valor_puntos = models.IntegerField()

    def __str__(self):
        return f"Linea {self.id_linea_pedido} de pedido {self.pedido}"


class Cupon(models.Model):
    id_cupon = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=256, unique=True)
    descuento = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_expiracion = models.DateField()
    disponibilidad = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo


class Reclamo(models.Model):
    id_reclamo = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="reclamos")
    descripcion = models.TextField()
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación del pedido (1 = Muy malo, 5 = Excelente)",
        default=3  # Valor predeterminado
    )

    def __str__(self):
        return f"Reclamo {self.id_reclamo} del Pedido {self.pedido.id_pedido}"

class ClienteNoRegistrado(models.Model):
    nombre = models.CharField(max_length=256)
    telefono = models.CharField(max_length=15)
    ubicacion = models.CharField(max_length=512)
    correo = models.EmailField(max_length=256, blank=True, null=True)

    def __str__(self):
        return f"Cliente No Registrado: {self.nombre}"

class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carrito', null=True, blank=True)
    session_id = models.CharField(max_length=255, null=False, blank=True,default=0)

    def __str__(self):
        return f"Carrito de {self.usuario.username if self.usuario else self.session_id}"

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name="items", on_delete=models.CASCADE)
    platillo = models.ForeignKey(Platillo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.platillo.nombre}"

    def actualizar_total(self):
        """Método para actualizar el total del item"""
        self.total = self.cantidad * self.precio_unitario
        self.save()
