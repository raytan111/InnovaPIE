from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

def vista_login(request):
    if request.method == 'POST':
        username = request.POST['User']
        password = request.POST['Contraseña']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # El usuario y la contraseña son correctos, realiza el inicio de sesión
            login(request, user)
            return redirect('home')
        else:
            # El usuario o la contraseña son incorrectos, muestra un mensaje de error
            error_message = 'Usuario o contraseña incorrectos.'
            return render(request, 'index/portal.html', {'error_message': error_message})

    return render(request, 'index/portal.html')

#Recuperar contraseña
def recuperar_clave(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            messages.error(request, 'El correo electrónico no está registrado.')
            return render(request, 'index/recuperar.html')
        
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        # Aquí, puedes verificar si el correo electrónico existe en tu base de datos.
        # Si no existe, puedes enviar un mensaje de error al usuario.

        # Personaliza el mensaje
        subject = 'Instrucciones para Recuperar tu Contraseña'
        message = render_to_string('index/email_recovery_template.txt', {
            'user': email,  # Aquí, en lugar de email, puedes pasar un objeto de usuario si lo tienes.
            'domain': request.get_host(),
            'token': token,
            'uid': user.id,
        })
        
        # Enviar correo
        send_mail(subject, message, 'noreply@tudominio.com', [email])
        
        messages.success(request, 'Se han enviado las instrucciones a tu correo electrónico.')
        return redirect('login')
    
    return render(request, 'index/recuperar.html')

def cambiar_clave(request, user_id, token):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'El usuario no existe.')
        return redirect('login')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            if PasswordResetTokenGenerator().check_token(user, token):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Contraseña actualizada con éxito.')
                return redirect('login')
            else:
                messages.error(request, 'El token no es válido.')
        else:
            messages.error(request, 'Las contraseñas no coinciden.')

    context = {
        'user': user,
        'token': token
    }
    return render(request, 'index/contraseña-reset.html', context)