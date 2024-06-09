from django.db.models import Model, CharField, SlugField, FloatField, ImageField, ForeignKey, \
    CASCADE, TextChoices, IntegerField, ManyToManyField, DateTimeField
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
    class StockType(TextChoices):
        AVAILABLE = 'available', 'Available'
        SOLD = 'sold', 'Sold'

    stock = CharField(max_length=10, choices=StockType.choices, default=StockType.AVAILABLE)
    title = CharField(max_length=255)
    slug = SlugField(max_length=255, editable=False)
    price = FloatField(db_default=0.0)
    description = CKEditor5Field('Text', config_name='extends')
    shopping_cost = FloatField()
    category = ForeignKey('apps.Category', on_delete=CASCADE)
    image = ImageField(upload_to='product/')
    count = IntegerField(db_default=0)
    like = ManyToManyField('users.User', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Order(Model):
    class StatusType(TextChoices):
        CREATED = 'created', 'Created'
    product = ForeignKey('apps.Product', on_delete=CASCADE)
    user = ForeignKey('users.User', on_delete=CASCADE)
    status = CharField(max_length=30, choices=StatusType.choices, default=StatusType.CREATED)
    created_at = DateTimeField(auto_now_add=True)






