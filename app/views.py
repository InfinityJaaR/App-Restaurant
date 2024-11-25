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