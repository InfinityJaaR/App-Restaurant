from django.db import models
from django.contrib.auth.models import User 
from django.core.validators import MinValueValidator, MaxValueValidator

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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pedidos")
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

    def __str__(self):
        return f"Pedido {self.id_pedido} de {self.usuario}"


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
