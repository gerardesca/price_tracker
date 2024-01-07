from django.contrib.auth.tokens import default_token_generator
from django.http.response import HttpResponse as HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import HttpResponseRedirect
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView, FormView
from django.views.generic.base import TemplateView
from django.contrib.auth.views import (
    LoginView, 
    PasswordResetView, 
    PasswordResetConfirmView,
    PasswordChangeView,
)

from .forms import (
    UserModel,
    LoginForm, 
    PassChangeForm, 
    PassResetForm, 
    SetPassForm, 
    UserUpdateForm,
    UserDeleteForm,
    RegisterForm,
    EmailChangeForm,
)


# auth
class AccountLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'¡Bienvenido <b>{form.get_user()}</b>!')
        return super().form_valid(form)


# password
class PassChangeView(SuccessMessageMixin, PasswordChangeView):
    form_class = PassChangeForm
    template_name = 'accounts/password_change_form.html'
    success_url = reverse_lazy("account:profile")
    success_message = "¡Contraseña actualizada!"


class PassResetView(SuccessMessageMixin, PasswordResetView):
    form_class = PassResetForm
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'emails/password_reset_email.html'
    success_url = reverse_lazy("core:home")
    success_message = ("Le enviamos instrucciones por correo electrónico para configurar su contraseña, "
                        "si existe una cuenta con el correo electrónico que ingresó. Debería recibirlos en breve. "
                        "Si no recibe un correo electrónico, asegúrese de haber ingresado la dirección con la que se registró y "
                        "verifique su carpeta de correo no deseado."
                        )

    
class PassResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    form_class = SetPassForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy("account:login")
    success_message = "¡Se ha actualizado su contraseña!. Ahora puede continuar e ingresar."


# profile
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    
class ProfileUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy("account:profile")
    success_message = "¡Información Actualizada!"
    
    
class ProfileDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = get_user_model()
    form_class = UserDeleteForm
    template_name = 'accounts/profile_delete.html'
    success_url = reverse_lazy("core:home")
    success_message = "Lamentamos que te vayas."
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {'username': self.request.user.username}
        return kwargs
    

# register
class RegisterView(SuccessMessageMixin, FormView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy("account:login")
    success_message = '¡Bienvenido! Revisa tu correo electronico y sigue las instrucciones.'

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "request": self.request,
        }
        
        form.save(**opts)
        return super().form_valid(form)


INTERNAL_ACTIVATION_SESSION_TOKEN = "_account_activation_token"

class RegisterConfirmView(TemplateView):
    template_name = 'accounts/register_confirm.html' 
    reset_url_token = "activation"
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.validlink = False
        self.user = get_user(kwargs["uidb64"])
        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_ACTIVATION_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                token_valid = self.token_generator.check_token(self.user, token)
                if token_valid:
                    # Store the token in the session and redirect to the
                    # view at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_ACTIVATION_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context["validlink"] = True
            del self.request.session[INTERNAL_ACTIVATION_SESSION_TOKEN]
            self.user.is_active = True
            self.user.save()
        else:
            context["validlink"] = False
        return context


# email
class EmailChangeView(SuccessMessageMixin, FormView):
    template_name = 'accounts/email_change_form.html'
    form_class = EmailChangeForm
    success_url = reverse_lazy("account:profile")
    success_message = "¡Verifica el correo para que se actualizado!"
    
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        self.user = self.request.user
        return super().dispatch(*args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs
    
    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "request": self.request,
        }
        
        form.save(**opts)
        return super().form_valid(form)
    

class EmailChangeConfirmView(TemplateView):
    template_name = 'accounts/email_change_confirm.html'
    reset_url_token = "email-validation"
    token_generator = default_token_generator
    
    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        if "uidb64" not in kwargs or "token" not in kwargs or "email" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' 'token'and 'email' parameters."
            )

        self.validlink = False
        self.user = get_user(kwargs["uidb64"])
        self.email = urlsafe_base64_decode(kwargs["email"]).decode()
        
        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_ACTIVATION_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                token_valid = self.token_generator.check_token(self.user, token)
                if token_valid:
                    # Store the token in the session and redirect to the
                    # view at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_ACTIVATION_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context["validlink"] = True
            del self.request.session[INTERNAL_ACTIVATION_SESSION_TOKEN]
            self.user.email = self.email
            self.user.save()
        else:
            context["validlink"] = False
        return context
    

def get_user(uidb64):
    try:
        # urlsafe_base64_decode() decodes to bytestring
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except (
        TypeError,
        ValueError,
        OverflowError,
        UserModel.DoesNotExist,
        ValidationError,
    ):
        user = None
    return user