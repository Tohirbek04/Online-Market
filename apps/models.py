from django.db.models import Model, CharField, SlugField, FloatField, ImageField, ForeignKey, \
    CASCADE, TextChoices, IntegerField, DateTimeField
from django.template.defaultfilters import slugify
from django_ckeditor_5.fields import CKEditor5Field

from apps.managers import ProductCountManager


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
    class StockType(TextChoices):
        AVAILABLE = 'available', 'Available'
        SOLD = 'sold', 'Sold'

    stock = CharField(max_length=10, choices=StockType.choices, default=StockType.AVAILABLE)
    title = CharField(max_length=255)
    slug = SlugField(max_length=255, editable=False)
    price = FloatField(db_default=0.0)
    description = CKEditor5Field('Text', config_name='extends')
    shopping_cost = FloatField()
    category = ForeignKey('apps.Category', CASCADE)
    image = ImageField(upload_to='product/images')
    count = IntegerField(db_default=0)
    objects = ProductCountManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_in_stock(self):
        return self.count > 0

    @property
    def total_sum(self):
        return self.shopping_cost + self.price


class Order(Model):
    class Status(TextChoices):
        CREATED = 'created', 'Created'

    product = ForeignKey('apps.Product', CASCADE, null=True, blank=True)
    user = ForeignKey('users.User', CASCADE, null=True, blank=True)
    status = CharField(max_length=30, choices=Status.choices, default=Status.CREATED)
    phone_number = CharField(max_length=9) # 901001010
    name = CharField(max_length=30)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class LikeModel(Model):
    user = ForeignKey('users.User', CASCADE)
    product = ForeignKey('apps.Product', CASCADE)
    created_at = DateTimeField(auto_now_add=True)
