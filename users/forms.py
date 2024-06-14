from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.forms import CharField, PasswordInput, ModelForm
import re
from users.models import User


class CreateForm(UserCreationForm):
    password1 = CharField(max_length=20, widget=PasswordInput)
    password2 = CharField(max_length=20, widget=PasswordInput)

    class Meta:
        model = User
        fields = 'phone', 'password1', 'password2'

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', )
        phone_number = ''.join(re.findall(r'\d', phone))
        return phone_number[3:]


class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = 'phone', 'password'

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = ''.join(re.findall(r'\d', phone))
        return phone[3:]

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


class PasswordUpdateForm(ModelForm):
    old_password = CharField(max_length=20, widget=PasswordInput)
    new_password = CharField(max_length=20, widget=PasswordInput)
    conform_password = CharField(max_length=20, widget=PasswordInput)

    class Meta:
        model = User
        fields = 'password',
