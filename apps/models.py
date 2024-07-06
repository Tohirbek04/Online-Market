from django.db.models import (CASCADE, SET_NULL, BooleanField, CharField,
                              DateTimeField, ForeignKey, ImageField,
                              IntegerField, Model, SlugField, TextChoices, DateField, CheckConstraint, Q, F)
from django.template.defaultfilters import slugify
from django_ckeditor_5.fields import CKEditor5Field

from users.models import User


class Category(Model):
    image = ImageField(upload_to='category/', null=True, blank=True)
    name = CharField(max_length=30, unique=True)
    slug = SlugField(max_length=30, editable=False)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

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
    category = ForeignKey('apps.Category', CASCADE, 'products')
    image = ImageField(upload_to='product/images')
    count = IntegerField(db_default=0)
    extra_balance = IntegerField(db_default=0)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            CheckConstraint(check=Q(price__gt=F('extra_balance')), name='price_gt_extra_balance'),
        ]

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
    updated_at = DateTimeField(auto_now=True)
    stream = ForeignKey('apps.Stream', SET_NULL, null=True, blank=True, related_name='orders')
    courier = ForeignKey('users.User', SET_NULL, null=True, blank=True, related_name='courier',
                         limit_choices_to={'type': User.Type.COURIER})
    region = ForeignKey('users.Region', SET_NULL, null=True, blank=True)
    district = ForeignKey('users.District', SET_NULL, null=True, blank=True)
    operator = ForeignKey('users.User', SET_NULL, null=True, blank=True, related_name='operator',
                          limit_choices_to={'type': User.Type.OPERATOR})
    send_order_date = DateField(null=True, blank=True)
    location = CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        site = SiteSetting.objects.first()
        if self.status == self.Status.DELIVERED and self.referral_user:
            _user = self.referral_user
            _user.balance += (self.product.extra_balance - self.stream.discount) * self.quantity
            _user.save()
        if self.status == self.Status.DELIVERED and self.operator:
            self.operator.refresh_from_db()
            self.operator.balance += site.operator_sum
            self.operator.save()
        if self.status == self.Status.DELIVERED and self.courier:
            self.courier.refresh_from_db()
            balance = self.courier.balance
            self.courier.balance += site.shopping_cost
            self.courier.save()
        super().save(force_insert, force_update, using, update_fields)

    @property
    def current_price(self):
        if self.stream and self.stream.discount:
            return self.product.price - hasattr(self.stream, 'discount') * self.stream.discount

    @property
    def current_total_price(self):
        if self.stream.discount:
            return self.quantity * (self.product.price - hasattr(self.stream, 'discount') * self.stream.discount)

    def __str__(self):
        return self.name


class LikeModel(Model):
    user = ForeignKey('users.User', CASCADE, related_name='likes')
    product = ForeignKey('apps.Product', CASCADE)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Like'


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


class SiteSetting(Model):
    operator_sum = IntegerField(verbose_name='operator uchun beriladigan pul')
    text = CKEditor5Field(null=True, blank=True, config_name='extends')
    shopping_cost = IntegerField(verbose_name='curyer uchun beriladigan pul')
    min_sum = IntegerField(verbose_name='eng kam yechib olish mumkin bolgan pul')

    class Meta:
        verbose_name = 'Site Setting'


class Transaction(Model):
    class Status(TextChoices):
        PROCESS = 'process', 'Process'
        CANCELED = 'canceled', 'Canceled'
        PAID = 'paid', 'Paid'

    user = ForeignKey('users.User', SET_NULL, null=True)
    status = CharField(max_length=10, choices=Status.choices, default=Status.PROCESS)
    card_number = CharField(max_length=16)
    amount = IntegerField(db_default=0)
    created_at = DateTimeField(auto_now_add=True)
    update_at = DateTimeField(auto_now=True)
    text = CKEditor5Field('Text', config_name='extends', null=True, blank=True)
    chek = ImageField(upload_to='apps/transaction', null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk and self.status == self.Status.PROCESS:
            self.user.balance -= self.amount
            self.user.save()
        super().save(force_insert, force_update, using, update_fields)
