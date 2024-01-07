from django.contrib.auth.tokens import default_token_generator


from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _

UserModel = get_user_model()


def get_user(uidb64):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except:
        return None
    

def validate_token_email(uidb64, token):
    user = get_user(uidb64)
    token_active = default_token_generator.check_token(user, token)
    
    if user is not None and token_active:
        return (True, user)
    else:
        return (False, None)


# email
def send_activation_email(request, user, to_email):
    
    subject = 'Verificación de cuenta'
    message = render_to_string(
        template_name="emails/activate_account.html",
        context={
            'user': user.username,
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user=user),
            'protocol': 'https' if request.is_secure() else 'http'
        }
    )
    
    email = EmailMessage(subject, message, to=[to_email])
    
    if email.send():
        messages.success(request, f'Para completar tu registro, verifica tu correo electrónico <b>{to_email}</b>')
        messages.success(request, f'Revisa tu bandeja de entrada y sigue las instrucciones del correo que te enviamos. \
                                    Si no lo encuentras, revisa tu carpeta de spam.')
    else:
        messages.error(request, f'Hubo un error al enviar correo a <b>{to_email}</b>')
    