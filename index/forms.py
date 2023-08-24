from django import forms    
from django.forms import ModelForm
from .models import *
from django.contrib.auth.models import User,Group

class ClienteForm(ModelForm):
    tipo_colegio = forms.ChoiceField(choices=(('', 'Selecciona una opción'), ('Escuela', 'Escuela'), ('Liceo', 'Liceo'), ('Jardin', 'Jardín')))

    class Meta:
        model = Cliente
        fields = ('tipo_colegio', 'nombre', 'correo', 'telefono', 'colegio', 'direccion', 'ciudad', 'comuna')

class ServicioForm(ModelForm):
    class Meta:
        model = Servicio
        fields = ('codigo','descripcion','precio','profesional')

class NuevoUsuarioForm(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirmar contraseña')
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label='Grupo')

    class Meta:
        model = User
        fields = ['username', 'password','email']

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        
        if password and password2 and password != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            user.groups.add(self.cleaned_data["group"])
        return user

class EditUsuarioForm(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirmar contraseña')
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), label='Grupos')

    class Meta:
        model = User
        fields = ['username', 'password', 'is_active', 'groups','email']

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        
        if password and password2 and password != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            user.groups.clear()  # Limpiar los grupos existentes
            user.groups.set(self.cleaned_data["groups"])
        return user

class PerfilUsuarioForm(forms.ModelForm):
    PROFESION_CHOICES = (
        ('', 'Selecciona una profesión'),
        ('Pediatra', 'Pediatra'),
        ('Médico Familiar', 'Médico Familiar'),
        ('Neurólogo', 'Neurólogo'),
        ('Psicólogo', 'Psicólogo'),
        ('Fonoaudiólogo', 'Fonoaudiólogo'),
        ('Ed. Diferencial', 'Ed. Diferencial'),
        ('Psicopedagogo', 'Psicopedagogo'),
        ('Terapeuta Ocupacional', 'Terapeuta Ocupacional'),
        ('Relator', 'Relator'),
        ('Asesor', 'Asesor'),
        ('Construcción', 'Construcción'),
        ('Material educativo', 'Material educativo')
    )

    profesion = forms.ChoiceField(choices=PROFESION_CHOICES)

    class Meta:
        model = PerfilUsuario
        fields = ['foto', 'rut', 'nombre', 'apellidop', 'apellidom', 'direccion', 'comuna', 'correo', 'telefono', 'profesion', 'descripcion', 'fecha_nacimiento', 'nombre_emergencia','contacto_emergencia', 'parentesco_emergencia']

class DatosTransferenciaForm(forms.ModelForm):
    class Meta:
        model = DatosTransferencia
        fields = ['d_nombre', 'd_rut', 'd_correo', 'd_banco', 'd_tipo_cuenta', 'd_numero_cuenta']

