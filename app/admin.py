from django.contrib import admin
from .models import Puntos, Estado, Platillo, Pedido, LineaPedidos, Cupon, Reclamo, MasCampos, ClienteNoRegistrado

# Registrar los modelos en el admin
admin.site.register(Puntos)
admin.site.register(Estado)
admin.site.register(Platillo)
admin.site.register(Pedido)
admin.site.register(LineaPedidos)
admin.site.register(Cupon)
admin.site.register(Reclamo)
admin.site.register(MasCampos)
admin.site.register(ClienteNoRegistrado)