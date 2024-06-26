from django.db.models import OneToOneField, CASCADE
from django.utils.translation import gettext_lazy as _
from users.managers import (AdminProxyManager, ClientProxyManager,
                            CourierProxyManager, ManagerProxyManager,
                            OperatorProxyManager)
from users.models import User


class OperatorProxyModel(User):
    objects = OperatorProxyManager()

    class Meta:
        proxy = True
        verbose_name = 'Operator'
        verbose_name_plural = 'Operators'


class ClientProxyModel(User):
    objects = ClientProxyManager()

    class Meta:
        proxy = True
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'


class ManagerProxyModel(User):
    objects = ManagerProxyManager()

    class Meta:
        proxy = True
        verbose_name = 'Manager'
        verbose_name_plural = 'Managers'


class AdminProxyModel(User):
    objects = AdminProxyManager()

    class Meta:
        proxy = True
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'


class CourierProxyModel(User):
    objects = CourierProxyManager()

    class Meta:
        proxy = True
        verbose_name = 'Courier'
        verbose_name_plural = 'Couriers'


class ReportProxy(User):
    class Meta:
        proxy = True
        verbose_name = _('User balance report')
        verbose_name_plural = _('User balance reports')
