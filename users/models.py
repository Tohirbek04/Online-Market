from django.contrib.auth.models import AbstractUser
from django.db.models import (CASCADE, BigIntegerField, CharField, ForeignKey,
                              ImageField, IntegerField, Model, SlugField, Sum,
                              TextChoices)
from django.template.defaultfilters import slugify
from django_ckeditor_5.fields import CKEditor5Field

from users.managers import UserModelManager


class Region(Model):
    name = CharField(max_length=30)
    slug = SlugField(max_length=30, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class District(Model):
    name = CharField(max_length=30)
    slug = SlugField(max_length=30, editable=False)
    region = ForeignKey('users.Region', on_delete=CASCADE)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Type(TextChoices):
        OPERATOR = 'operator', 'Operator'
        MANAGER = 'manager', 'Manager'
        ADMIN = 'admin', 'Admin'
        CLIENT = 'client', 'Client'
        COURIER = 'courier', 'Courier'

    balance = IntegerField(db_default=0)
    type = CharField(max_length=10, choices=Type.choices, default=Type.CLIENT)
    username = None
    phone = CharField(max_length=20, unique=True)
    image = ImageField(upload_to='users/', null=True, blank=True)
    background_image = ImageField(upload_to='users/', null=True, blank=True)
    district = ForeignKey('users.District', CASCADE, null=True, blank=True)
    region = ForeignKey('users.Region', CASCADE, null=True, blank=True)
    telegram_id = BigIntegerField(null=True, blank=True)
    location = CharField(max_length=255, null=True, blank=True)
    about = CKEditor5Field('Text', config_name='extends', null=True, blank=True)

    USERNAME_FIELD = 'phone'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserModelManager()

    @property
    def is_operator(self):
        return self.type == self.Type.OPERATOR

    @property
    def get_paid_balance(self):
        return self.transaction_set.filter(status='paid').aggregate(summa=Sum('amount'))['summa']

# class Profile(Model):
#     user = OneToOneField('apps.User', CASCADE)
#     from_working_time = ''
#     to_working_time = ''
#     passport = ''
