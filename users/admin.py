from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User
from users.proxy import (AdminProxyModel, ClientProxyModel, CourierProxyModel,
                         ManagerProxyModel, OperatorProxyModel)


class UserModelAdmin(UserAdmin):
    list_display = 'id', 'phone', 'first_name', 'last_name'
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

    def save_model(self, request, obj: User, form, change):
        obj.type = self.type
        obj.is_staff = self.type == obj.Type.MANAGER
        super().save_model(request, obj, form, change)


@admin.register(OperatorProxyModel)
class OperatorModelAdmin(UserModelAdmin):
    type = User.Type.OPERATOR


@admin.register(ManagerProxyModel)
class ManagerModelAdmin(UserModelAdmin):
    type = User.Type.MANAGER


@admin.register(ClientProxyModel)
class ClientModelAdmin(UserModelAdmin):
    type = User.Type.CLIENT


@admin.register(CourierProxyModel)
class CourierModelAdmin(UserModelAdmin):
    type = User.Type.COURIER
