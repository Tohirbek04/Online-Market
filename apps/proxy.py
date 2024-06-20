from apps.managers import (ArchivedOrderManager, CancelledOrderManager,
                           DeliveredOrderManager, DeliveryOrderManager,
                           MissedCallOrderManager, NewOrderManager,
                           ReadyOrderManager)
from apps.models import Order


class NewOrderProxyModel(Order):
    objects = NewOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'New Order'
        verbose_name_plural = 'New Orders'


class ReadyOrderProxyModel(Order):
    objects = ReadyOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Ready Order'
        verbose_name_plural = 'Ready Orders'


class DeliveryOrderProxyModel(Order):
    objects = DeliveryOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Delivery Order'
        verbose_name_plural = 'Delivery Orders'


class DeliveredOrderProxyModel(Order):
    objects = DeliveredOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Delivered Order'
        verbose_name_plural = 'Delivered Orders'


class CancelledOrderProxyModel(Order):
    objects = CancelledOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Cancelled Order'
        verbose_name_plural = 'Cancelled Orders'


class ArchivedOrderProxyModel(Order):
    objects = ArchivedOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Archived Order'
        verbose_name_plural = 'Archived Orders'


class MissedCallOrderProxyModel(Order):
    objects = MissedCallOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'MissedCall Order'
        verbose_name_plural = 'MissedCall Orders'
