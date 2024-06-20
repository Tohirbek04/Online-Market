from django.db.models import (CASCADE, SET_NULL, BooleanField, CharField, DateTimeField, ForeignKey, ImageField,
                              IntegerField, Model, SlugField, TextChoices)
from django.template.defaultfilters import slugify
from django_ckeditor_5.fields import CKEditor5Field


class Category(Model):
    image = ImageField(upload_to='category/', null=True, blank=True)
    name = CharField(max_length=30, unique=True)
    slug = SlugField(max_length=30, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(Model):
    title = CharField(max_length=255)
    slug = SlugField(max_length=255, editable=False)
    price = IntegerField(db_default=0)
    description = CKEditor5Field('Text', config_name='extends')
    shopping_cost = IntegerField()
    category = ForeignKey('apps.Category', CASCADE, 'products')
    image = ImageField(upload_to='product/images')
    count = IntegerField(db_default=0)
    extra_balance = IntegerField(db_default=0)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_in_stock(self):
        return self.count > 0


class Order(Model):
    class Status(TextChoices):
        NEW = 'new', 'New',
        READY = 'ready', 'Ready',
        DELIVERY = 'delivery', 'Delivery',
        DELIVERED = 'delivered', 'Delivered',
        CANCELLED = 'cancelled', 'Cancelled',
        ARCHIVED = 'archived', 'Archived',
        MISSED_CALL = 'missed_call', 'MISSED CALL'

    referral_user = ForeignKey('users.User', SET_NULL, null=True, blank=True, related_name='referral_user')
    user = ForeignKey('users.User', SET_NULL, null=True, blank=True, related_name='orders')
    product = ForeignKey('apps.Product', CASCADE, null=True, blank=True, related_name='orders')
    status = CharField(max_length=30, choices=Status.choices, default=Status.NEW)
    quantity = IntegerField(default=1)
    phone_number = CharField(max_length=20)
    name = CharField(max_length=30)
    description = CKEditor5Field(null=True, blank=True, config_name='extends')
    created_at = DateTimeField(auto_now_add=True)
    stream = ForeignKey('apps.Stream', SET_NULL, null=True, blank=True, related_name='orders')
    courier = ForeignKey('users.User', SET_NULL, null=True, blank=True, related_name='courier')
    operator = ForeignKey('users.User', SET_NULL, null=True, blank=True, related_name='operator')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.name


class LikeModel(Model):
    user = ForeignKey('users.User', CASCADE, related_name='likes')
    product = ForeignKey('apps.Product', CASCADE)
    created_at = DateTimeField(auto_now_add=True)


class Stream(Model):
    name = CharField(max_length=20)
    discount = IntegerField(default=0)
    owner = ForeignKey('users.User', CASCADE)
    product = ForeignKey('apps.Product', CASCADE, related_name='streams')
    views_count = IntegerField(db_default=0)


class Competition(Model):
    name = CharField(max_length=255, unique=True)
    start_date = DateTimeField(null=True, blank=True)
    end_date = DateTimeField(null=True, blank=True)
    is_active = BooleanField(db_default=False)

    def __str__(self):
        return self.name


class Setting(Model):
    operator_sum = IntegerField()
    text = CKEditor5Field(null=True, blank=True, config_name='extends')
    min_sum = IntegerField()
