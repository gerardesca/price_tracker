from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django import forms

from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm, 
    PasswordChangeForm,
    SetPasswordForm, 
    PasswordResetForm,
)


UserModel = get_user_model()
attr_class_form = 'form-control h-auto form-control-solid'


# auth
class LoginForm(AuthenticationForm):
    
    username = forms.CharField(
        widget=forms.TextInput(attrs = {'class': attr_class_form, 'placeholder': 'Nombre de usuario'}),
        label = '',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs = {'class': attr_class_form, 'placeholder': 'Constraseña'}),
        label = '',
    )
    

# password
class PassChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs = {'class': attr_class_form, 'placeholder': 'Contraseña'}),
        label='',
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs = {'class': attr_class_form, 'placeholder': 'Nueva contraseña'}),
        label='',
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs = {'class': attr_class_form, 'placeholder': 'Confirma nueva contraseña'}),
        label=''
    )
        

class PassResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs = {'class': attr_class_form, 'placeholder': 'Correo electrónico'}),
        label='',
    )
        
       
class SetPassForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs = {'class': attr_class_form, 'placeholder': 'Nueva contraseña'}),
        label='',
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs = {'class': attr_class_form, 'placeholder': 'Confirma nueva contraseña'}),
        label='',
    )
    

# profile
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs = {'class': attr_class_form, 'placeholder': 'Correo electrónico'}),
        label='', 
        required=True,
        disabled=True,
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs = {'class': attr_class_form, 'placeholder': 'Nombre'}),
        label='', 
        required=True, 
        max_length=100,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs = {'class': attr_class_form, 'placeholder': 'Apellido'}),
        label='', 
        required=False, 
        max_length=100,
    )

    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'email']
        
        
class UserDeleteForm(LoginForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs = {'class': attr_class_form, 'placeholder': 'Nombre de usuario'}),
        label = '',
        disabled=True,
    )
    
    error_messages = {
        "invalid_login": "La contraseña es incorrecta. Intenta de nuevo.",
    }



class SendEmailMixin:
    """
    Send a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        email_message.send()


# register    
class RegisterForm(UserCreationForm, SendEmailMixin):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs = {'class': attr_class_form, 'placeholder': 'Correo electrónico'}),
        label='', 
        required=True,
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs = {'class': attr_class_form, 'placeholder': 'Nombre'}),
        label='', 
        required=True, 
        max_length=100,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs = {'class': attr_class_form, 'placeholder': 'Apellido'}),
        label='', 
        required=False, 
        max_length=100,
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': attr_class_form, 'placeholder': 'Nombre de usuario'}),
        label='',
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': attr_class_form, 'placeholder': 'Contraseña'}),
        label='',
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': attr_class_form, 'placeholder': 'Confirmación de Contraseña'}),
        label='',
    )


    class Meta:
        model = UserModel
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
        
    def save(
        self,
        commit=True,
        domain_override=None,
        use_https=False,
        token_generator=default_token_generator,
        request=None,
        extra_email_context=None,
    ):
        
        user = super().save(commit=False)
        user.is_active = False
        if commit:
            user.save()
            
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = UserModel.get_email_field_name()
        
        user_email = getattr(user, email_field_name)
        context = {
            "email": user_email,
            "domain": domain,
            "site_name": site_name,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            "token": token_generator.make_token(user),
            "protocol": "https" if use_https else "http",
            **(extra_email_context or {}),
        }
        self.send_mail(
            subject_template_name="emails/activate_account_subject.txt",
            email_template_name="emails/account_activate_email.html",
            context=context,
            from_email=None,
            to_email=user_email,
            html_email_template_name=None,
        )


# email
class EmailChangeForm(forms.Form, SendEmailMixin):
    
    error_messages = {
        "email_equal": "El correo electrónico es el mismo de tu cuenta.",
        "email_exists": "El correo electrónico ya existe."
    }
    
    new_email = forms.EmailField(
        widget=forms.EmailInput(attrs = {'class': attr_class_form, 'placeholder': 'Ingresa nuevo correo electrónico'}),
        label='',
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        
        
    def clean_new_email(self):
        email = self.user.email
        new_email = self.cleaned_data.get("new_email")
        
        email_field_name = UserModel.get_email_field_name()
        emails = UserModel._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: new_email,
                "is_active": True,
            }
        )
        
        if email == new_email:
            raise ValidationError(
                self.error_messages["email_equal"],
                code="email_equal",
            )
        
        if len(emails) != 0:
            raise ValidationError(
                self.error_messages["email_exists"],
                code="email_exists",
            )
            
        return new_email
    
    
    def save(
        self,
        domain_override=None,
        use_https=False,
        token_generator=default_token_generator,
        request=None,
        extra_email_context=None,
    ):
        
        user = self.user
            
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        
        new_email = self.clean_new_email()
        context = {
            "email": urlsafe_base64_encode(force_bytes(new_email)),
            "domain": domain,
            "site_name": site_name,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            "token": token_generator.make_token(user),
            "protocol": "https" if use_https else "http",
            **(extra_email_context or {}),
        }
        self.send_mail(
            subject_template_name="emails/email_change_subject.txt",
            email_template_name="emails/account_activate_email.html",
            context=context,
            from_email=None,
            to_email=new_email,
            html_email_template_name=None,
        )
