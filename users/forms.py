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


class PasswordUpdateForm(Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    old_password = CharField(max_length=20, widget=PasswordInput, label="Old Password")
    new_password = CharField(max_length=20, widget=PasswordInput, label="New Password")
    confirm_password = CharField(max_length=20, widget=PasswordInput, label="Confirm New Password")

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', "New password and confirm password do not match.")
        self.user = authenticate(phone=self.request.phone, password=old_password)
        if not self.user:
            self.add_error('old_password', "Old password is incorrect.")

        return cleaned_data

    def save(self):
        user = self.user.save(commit=False)
        user.set_password(self.cleaned_data['new_password'])
        user.save()
        return user


class UpdateModelForm(ModelForm):
    region = ModelChoiceField(queryset=Region.objects.all(), required=False)
    district = ModelChoiceField(queryset=District.objects.all(), required=False)

    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'region', 'district', 'about'

