from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.models import (Category, Competition, LikeModel, Product,
                         SiteSetting, Stream)
from apps.proxy import (ArchivedOrderProxyModel, CancelledOrderProxyModel,
                        ClientTransactionProxyModel, DeliveredOrderProxyModel,
                        DeliveryOrderProxyModel, MissedCallOrderProxyModel,
                        NewOrderProxyModel, OperatorTransactionProxyModel,
                        OrderHistoryProxyModel, ReadyOrderProxyModel,
                        TransactionCancelledProxyModel,
                        TransactionPaidProxyModel,
                        TransactionProcessProxyModel)


@admin.register(Category)
class CategoryModelAdmin(ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Product)
class Product(ModelAdmin):
    list_display = ['id', 'title', 'price', 'count', 'extra_balance']


@admin.register(OrderHistoryProxyModel)
class OrderHistoryModelAdmin(ModelAdmin):
    list_display = ['id', 'name', 'status', 'product_title',
                    'courier_first_name', 'operator_first_name', 'phone_number']

    def courier_first_name(self, obj):
        return obj.courier.first_name if obj.courier else ''

    def operator_first_name(self, obj):
        return obj.operator.first_name if obj.operator else ''

    def product_title(self, obj):
        return obj.product.title if obj.product else ''

    def stream_name(self, obj):
        return obj.stream.name if obj.stream else ''

    stream_name.short_description = 'Stream owner'
    product_title.short_description = 'Product name'
    courier_first_name.short_description = 'Courier first name'
    operator_first_name.short_description = 'Operator first name'


@admin.register(NewOrderProxyModel)
class NewOrderProxyModelAdmin(ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'product_name', 'created_at']

    def product_name(self, obj):
        return obj.product.title

    product_name.short_description = 'product name'


@admin.register(ReadyOrderProxyModel)
class ReadyOrderProxyModelAdmin(ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'product_name', 'created_at']

    def product_name(self, obj):
        return obj.product.title

    product_name.short_description = 'product name'


@admin.register(DeliveryOrderProxyModel)
class DeliveryOrderProxyModelAdmin(ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'product_name', 'created_at']

    def product_name(self, obj):
        return obj.product.title

    product_name.short_description = 'product name'


@admin.register(DeliveredOrderProxyModel)
class DeliveredOrderProxyModelAdmin(ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'product_name', 'created_at']

    def product_name(self, obj):
        return obj.product.title

    product_name.short_description = 'product name'


@admin.register(CancelledOrderProxyModel)
class CancelledOrderProxyModelAdmin(ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'product_name', 'created_at']

    def product_name(self, obj):
        return obj.product.title

    product_name.short_description = 'product name'


@admin.register(MissedCallOrderProxyModel)
class MissedCallOrderProxyModelAdmin(ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'product_name', 'created_at']

    def product_name(self, obj):
        return obj.product.title

    product_name.short_description = 'product name'


@admin.register(ArchivedOrderProxyModel)
class ArchivedOrderModelAdmin(ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'product_name', 'created_at']

    def product_name(self, obj):
        return obj.product.title

    product_name.short_description = 'product name'


@admin.register(Competition)
class CompetitionModelAdmin(ModelAdmin):
    list_display = ['id', 'name', 'is_active']


@admin.register(SiteSetting)
class SettingsModelAdmin(ModelAdmin):
    list_display = ['id', 'operator_sum', 'min_sum', 'shopping_cost']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Stream)
class StreamModelAdmin(ModelAdmin):
    list_display = ['id', 'name', 'discount', 'product_name']

    def product_name(self, obj):
        return obj.product.title

    product_name.short_description = 'product name'


@admin.register(LikeModel)
class LikeModelAdmin(ModelAdmin):
    list_display = ['id', 'product_name']

    def product_name(self, obj):
        return obj.product.title

    product_name.short_description = 'product name'


class TransactionModelAdmin(ModelAdmin):
    list_display = 'id', 'amount', 'update_at', 'status'

    def user(self, obj):
        return obj.user.first_name

    user.short_description = 'User'


@admin.register(TransactionPaidProxyModel)
class TransactionPaidModelAdmin(TransactionModelAdmin):
    pass


@admin.register(TransactionProcessProxyModel)
class TransactionProcessModelAdmin(TransactionModelAdmin):
    pass


@admin.register(TransactionCancelledProxyModel)
class TransactionCancelledModelAdmin(TransactionModelAdmin):
    pass


@admin.register(OperatorTransactionProxyModel)
class OperatorTransactionModelAdmin(ModelAdmin):
    list_display = 'id', 'amount', 'update_at', 'status'

    def user(self, obj):
        return obj.user.first_name

    user.short_description = 'User'


@admin.register(ClientTransactionProxyModel)
class ClientTransactionModelAdmin(OperatorTransactionModelAdmin):
    pass
