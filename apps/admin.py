from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.models import Category, Product, Order
from apps.proxy import NewOrderProxyModel, ReadyOrderProxyModel, DeliveryOrderProxyModel, \
    DeliveredOrderProxyModel, CancelledOrderProxyModel, MissedCallOrderProxyModel


@admin.register(Category)
class CategoryModelAdmin(ModelAdmin):
    pass


@admin.register(Product)
class Product(ModelAdmin):
    pass


@admin.register(Order)
class OrderModelAdmin(ModelAdmin):
    pass


@admin.register(NewOrderProxyModel)
class NewOrderProxyModelAdmin(ModelAdmin):
    pass

@admin.register(ReadyOrderProxyModel)
class ReadyOrderProxyModelAdmin(ModelAdmin):
    pass


@admin.register(DeliveryOrderProxyModel)
class DeliveryOrderProxyModelAdmin(ModelAdmin):
    pass


@admin.register(DeliveredOrderProxyModel)
class DeliveredOrderProxyModelAdmin(ModelAdmin):
    pass


@admin.register(CancelledOrderProxyModel)
class CancelledOrderProxyModelAdmin(ModelAdmin):
    pass


@admin.register(MissedCallOrderProxyModel)
class MissedCallOrderProxyModelAdmin(ModelAdmin):
    pass
