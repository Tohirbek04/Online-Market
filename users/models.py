from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, TextChoices, ImageField, BigIntegerField
from django_ckeditor_5.fields import CKEditor5Field

from users.managers import UserModelManager


class User(AbstractUser):
    class Type(TextChoices):
        OPERATOR = 'operator', 'Operator'
        MANAGER = 'manager', 'Manager'
        ADMIN = 'admin', 'Admin'
        CLIENT = 'client', 'Client'

    type = CharField(max_length=10, choices=Type.choices, default=Type.CLIENT)
    username = None
    phone = CharField(max_length=20, unique=True)
    image = ImageField(upload_to='users/', null=True, blank=True)
    background_image = ImageField(upload_to='users/', null=True, blank=True)
    district = CharField(max_length=50, null=True, blank=True)
    region = CharField(max_length=50, null=True, blank=True)
    telegram_id = BigIntegerField(null=True, blank=True)
    location = CharField(max_length=255, null=True, blank=True)
    about = CKEditor5Field('Text', config_name='extends', null=True, blank=True)
    USERNAME_FIELD = 'phone'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserModelManager()
