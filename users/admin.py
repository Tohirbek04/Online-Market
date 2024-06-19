from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User
from users.proxy import (AdminProxyModel, ClientProxyModel, ManagerProxyModel,
                         OperatorProxyModel)


class UserModelAdmin(UserAdmin):
    list_display = 'id', 'phone'
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

    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("phone",)
    ordering = ("phone",)


@admin.register(OperatorProxyModel)
class OperatorModelAdmin(UserModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.type = User.Type.OPERATOR
        super().save_model(request, obj, form, change)


@admin.register(ManagerProxyModel)
class ManagerModelAdmin(UserModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.type = User.Type.MANAGER
        super().save_model(request, obj, form, change)


@admin.register(ClientProxyModel)
class ClientModelAdmin(UserModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.type = User.Type.CLIENT
        super().save_model(request, obj, form, change)


@admin.register(AdminProxyModel)
class AdminModelAdmin(UserModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.type = User.Type.ADMIN
        super().save_model(request, obj, form, change)
