import re

from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import CharField, ModelChoiceField, ModelForm, PasswordInput, Form

from users.models import District, Region, User


class CreateForm(UserCreationForm):
    password1 = CharField(max_length=20, widget=PasswordInput)
    password2 = CharField(max_length=20, widget=PasswordInput)

    class Meta:
        model = User
        fields = 'phone', 'password1', 'password2'


class LoginForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = 'phone', 'password'

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', )
        phone_number = ''.join(re.findall(r'\d', phone))
        return phone_number[3:]

    def clean(self):
        phone = self.cleaned_data.get('phone')
        password = self.cleaned_data.get('password')

        if phone and password:
            self.user_cache = authenticate(phone=phone, password=password)
            if self.user_cache is None:
                raise ValidationError("Invalid password or phone number")
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class UpdateModelForm(ModelForm):
    region = ModelChoiceField(queryset=Region.objects.all(), required=False)
    district = ModelChoiceField(queryset=District.objects.all(), required=False)

    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'region', 'district', 'about'


class ChangePasswordForm(Form):
    old_password = CharField(widget=PasswordInput())
    new_password = CharField(widget=PasswordInput())
    confirm_password = CharField(widget=PasswordInput())
