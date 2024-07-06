from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, F, Case, When, IntegerField, Q
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.admin import ClientTransactionModelAdmin
from apps.models import SiteSetting, Order
from apps.proxy import ClientTransactionProxyModel
from users.models import User, Account
from users.proxy import (ClientProxyModel, CourierProxyModel,
                         ManagerProxyModel, OperatorProxyModel, ReportProxy)


class UserModelAdmin(UserAdmin):
    show_full_result_count = False
    list_display = 'user_avatar', 'id', 'phone', 'first_name', 'last_name',
    filter_horizontal = ['groups', 'user_permissions']
    fieldsets = (
        (None, {"fields": ("password", "phone")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("My photo"), {"fields": ("image",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "password1", "password2"),
            },
        ),
    )

    class Media:
        js = (
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/jquery.inputmask/5.0.6/jquery.inputmask.min.js',
            'apps/custom/main.js',
        )

    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("phone",)
    ordering = ("phone",)
    readonly_fields = ['user_avatar']

    @admin.display(description='avatar')
    def user_avatar(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="40px" height="40px" alt="" style="border-radius: 50%;'
                             f' object-fit: cover; border: 2px solid #ddd; box-shadow: 0 0 5px rgba(0, 0, 0, 0.15);">')
        return mark_safe(f'<img src="apps" width="40px" height="40px" alt="" style="border-radius: 50%; '
                         f'object-fit: cover; border: 2px solid #ddd; box-shadow: 0 0 5px rgba(0, 0, 0, 0.15);">')

    def save_model(self, request, obj: User, form, change):
        obj.type = self.type
        super().save_model(request, obj, form, change)
        if self.type == obj.Type.MANAGER:
            obj.is_staff = True
            content_type = ContentType.objects.get_for_model(
                ClientTransactionProxyModel)  # TODO permission was not granted to the manager
            name = ClientTransactionProxyModel.__name__.lower()
            perm_codename_1 = f'change_{name}'
            perm_codename_2 = f'view_{name}'
            permissions = Permission.objects.filter(content_type=content_type,
                                                    codename__in=(perm_codename_1, perm_codename_2))
            obj.user_permissions.add(*permissions)
            obj.save()

    def get_queryset(self, request):
        return super().get_queryset(request).filter(type=self.type)


class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'account'


@admin.register(OperatorProxyModel)
class OperatorModelAdmin(UserModelAdmin):
    type = User.Type.OPERATOR
    inlines = AccountInline,
    fieldsets = (
        (None, {"fields": ("password", "phone")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("My photo"), {"fields": ("image",)}),
    )


@admin.register(ManagerProxyModel)
class ManagerModelAdmin(UserModelAdmin):
    type = User.Type.MANAGER


@admin.register(ClientProxyModel)
class ClientModelAdmin(UserModelAdmin):
    type = User.Type.CLIENT


@admin.register(CourierProxyModel)
class CourierModelAdmin(UserModelAdmin):
    type = User.Type.COURIER


@admin.register(Account)
class AccountModelAdmin(ModelAdmin):
    list_display = 'id', 'from_working_time', 'to_working_time', 'first_name'
    list_select_related = 'operator',

    @admin.action(description='First Name')
    def first_name(self, obj):
        return obj.operator.first_name


@admin.register(ReportProxy)
class UserBalanceReportModelAdmin(ModelAdmin):
    change_list_template = 'users/user_balance_report.html'
    list_filter = ("type",)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            queryset = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

        queryset = (
            Order.objects.annotate(
                referral_user_possibly_extra_balance=Sum(
                    Case(When(
                        Q(status=Order.Status.DELIVERY) &
                        Q(referral_user__isnull=False),
                        then=F('product__extra_balance') * F('quantity')
                    ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                referral_user_possibly_discount=Sum(
                    Case(When(
                        Q(status=Order.Status.DELIVERY) &
                        Q(stream__owner__isnull=False),
                        then=F('stream__discount') * F('quantity')
                    ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                referral_user_real_extra_balance=Sum(
                    Case(When(
                        Q(status=Order.Status.DELIVERED) &
                        Q(referral_user__isnull=False),
                        then=F('product__extra_balance') * F('quantity')
                    ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                referral_user_real_discount=Sum(
                    Case(When(
                        Q(status=Order.Status.DELIVERED) &
                        Q(stream__owner__isnull=False),
                        then=F('stream__discount') * F('quantity')
                    ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                operator_order_delivered=Sum(
                    Case(When(
                        Q(operator__isnull=False) &
                        Q(status=Order.Status.DELIVERED),
                        then=1
                    ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                operator_order_delivery=Sum(
                    Case(When(
                        Q(operator__isnull=False) &
                        Q(status=Order.Status.DELIVERY),
                        then=1
                    ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
            ).values(
                'referral_user_possibly_extra_balance',
                'referral_user_real_extra_balance',
                'referral_user_possibly_discount',
                'referral_user_real_discount',
                'operator_order_delivered',
                'operator_order_delivery'
            )
        )
        aggregation = queryset.aggregate(
            referral_user_total_possibly_extra_balance=Sum('referral_user_possibly_extra_balance'),
            referral_user_total_real_extra_balance=Sum('referral_user_real_extra_balance'),
            referral_user_total_real_discount=Sum('referral_user_real_discount'),
            referral_user_total_possibly_discount=Sum('referral_user_possibly_discount'),
            operator_order_delivered_count=Sum('operator_order_delivered'),
            operator_order_delivery_count=Sum('operator_order_delivery')
        )

        extra_context = {}
        extra_context.update(aggregation)

        site_setting = SiteSetting.objects.first()
        extra_context['operator_real_balance'] = (
                extra_context['operator_order_delivered_count'] * site_setting.operator_sum
        )
        extra_context['operator_possibly_balance'] = (
                extra_context['operator_order_delivery_count'] * site_setting.operator_sum
        )
        extra_context['referral_user_real_balance'] = (
                extra_context['referral_user_total_real_extra_balance']
                - extra_context['referral_user_total_real_discount']
        )
        extra_context['referral_user_possibly_balance'] = (
                extra_context['referral_user_total_possibly_extra_balance']
                - extra_context['referral_user_total_possibly_discount']
        )

        extra_context['total_real_balance'] = (extra_context['operator_real_balance']
                                               + extra_context['referral_user_real_balance'])
        extra_context['total_possibly_balance'] = (
                extra_context['operator_possibly_balance']
                + extra_context['referral_user_possibly_balance'])

        response.context_data.update(extra_context)
        return response
