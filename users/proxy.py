from users.managers import OperatorProxyManager, ClientProxyManager, ManagerProxyManager, AdminProxyManager
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
