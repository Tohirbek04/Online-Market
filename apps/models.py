from django.db.models import Model, CharField, SlugField, FloatField, ImageField, ForeignKey, \
    CASCADE, TextChoices, IntegerField, DateTimeField, SET_NULL
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
    price = FloatField(db_default=0.0)
    description = CKEditor5Field('Text', config_name='extends')
    shopping_cost = IntegerField()
    category = ForeignKey('apps.Category', CASCADE)
    image = ImageField(upload_to='product/images')
    count = IntegerField(db_default=0)
    extra_balance = IntegerField(db_default=0)

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
        NEW = 'new', 'New',
        VISIT = 'visit', 'Vist',
        READY = 'ready', 'Ready',
        DELIVERY = 'delivery', 'Delivery',
        DELIVERED = 'delivered', 'Delivered',
        CANCELLED = 'cancelled', 'Cancelled',
        ARCHIVED = 'archived', 'Archived',
        MISSED_CALL = 'missed_call', 'MISSED CALL'

    product = ForeignKey('apps.Product', CASCADE, null=True, blank=True)
    user = ForeignKey('users.User', CASCADE, null=True, blank=True)
    status = CharField(max_length=30, choices=Status.choices, default=Status.NEW)
    quantity = IntegerField(default=1)
    phone_number = CharField(max_length=20)
    name = CharField(max_length=30)
    description = CKEditor5Field(null=True, blank=True, config_name='extends')
    created_at = DateTimeField(auto_now_add=True)
    stream = ForeignKey('apps.Stream', null=True, blank=True, on_delete=SET_NULL)
    courier = ForeignKey('users.User', null=True, blank=True, on_delete=SET_NULL, related_name='courier')
    operator = ForeignKey('users.User', null=True, blank=True, on_delete=SET_NULL, related_name='operator')

    class Meta:
        ordering = ['created_at']


class LikeModel(Model):
    user = ForeignKey('users.User', CASCADE)
    product = ForeignKey('apps.Product', CASCADE)
    created_at = DateTimeField(auto_now_add=True)


class Stream(Model):
    name = CharField(max_length=20)
    discount = IntegerField(default=0)
    owner = ForeignKey('users.User', CASCADE, related_name='streams')
    product = ForeignKey('apps.Product', CASCADE, related_name='streams')


