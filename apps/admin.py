from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.translation import gettext_lazy as _

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
    list_select_related = 'courier', 'operator', 'product'
    show_full_result_count = False
    list_display = ['id', 'name', 'status', 'product_title',
                    'courier_first_name', 'operator_first_name', 'phone_number']

    @admin.action(description='Courier first name')
    def courier_first_name(self, obj):
        return obj.courier.first_name if obj.courier else ''

    @admin.action(description='Operator first name')
    def operator_first_name(self, obj):
        return obj.operator.first_name if obj.operator else ''

    @admin.action(description='Product name')
    def product_title(self, obj):
        return obj.product.title

    @admin.action(description='Stream owner')
    def stream_name(self, obj):
        return obj.stream.name


class ProxyOrderMixin(ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'product_name', 'created_at']
    list_select_related = 'product',
    show_full_result_count = False

    @admin.action(description='product name')
    def product_name(self, obj):
        return obj.product.title


@admin.register(NewOrderProxyModel)
class NewOrderProxyModelAdmin(ProxyOrderMixin):
    pass


@admin.register(ReadyOrderProxyModel)
class ReadyOrderProxyModelAdmin(ProxyOrderMixin):
    pass


@admin.register(DeliveryOrderProxyModel)
class DeliveryOrderProxyModelAdmin(ProxyOrderMixin):
    pass


@admin.register(DeliveredOrderProxyModel)
class DeliveredOrderProxyModelAdmin(ProxyOrderMixin):
    pass


@admin.register(CancelledOrderProxyModel)
class CancelledOrderProxyModelAdmin(ProxyOrderMixin):
    pass


@admin.register(MissedCallOrderProxyModel)
class MissedCallOrderProxyModelAdmin(ProxyOrderMixin):
    pass


@admin.register(ArchivedOrderProxyModel)
class ArchivedOrderModelAdmin(ProxyOrderMixin):
    pass


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
    list_select_related = 'product',

    @admin.action(description='product name')
    def product_name(self, obj):
        return obj.product.title


@admin.register(LikeModel)
class LikeModelAdmin(ModelAdmin):
    list_display = ['id', 'product_name']
    list_select_related = 'product',

    @admin.action(description='product name')
    def product_name(self, obj):
        return obj.product.title


class TransactionModelAdmin(ModelAdmin):
    list_display = 'id', 'amount', 'update_at', 'status', 'user'
    list_select_related = 'user',

    @admin.action(description='User')
    def user(self, obj):
        return obj.user.first_name


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
    list_display = 'id', 'amount', 'update_at', 'status', 'user'
    list_select_related = 'user',

    @admin.action(description='User')
    def user(self, obj:OperatorTransactionProxyModel):
        return obj.user.first_name


@admin.register(ClientTransactionProxyModel)
class ClientTransactionModelAdmin(OperatorTransactionModelAdmin):
    pass


def get_app_list(self, request):
    app_dict = self._build_app_dict(request)
    custom_order = [
        _('New Orders'),
        _('Ready Orders'),
        _('Delivery Orders'),
        _('Delivered Orders'),
        _('Cancelled Orders'),
        _('Missed Call Orders'),
        _('Archived Orders'),
        _('History Orders'),
        _('Processes Transactions'),
        _('Paid Transactions'),
        _('Cancelled Transactions'),
        _('Operator Transactions'),
        _('Client Transactions'),
        _('Streams'),
        _('Likes'),
        _('Categories'),
        _('Products'),
        _('Competitions'),
        _('Site Settings'),

    ]
    app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
    for app in app_list:
        if app['app_label'] == 'apps':
            app['models'].sort(key=lambda x: custom_order.index(x['name']))
    return app_list


admin.AdminSite.get_app_list = get_app_list
