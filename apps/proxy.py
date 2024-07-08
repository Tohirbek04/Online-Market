from django.utils.translation import gettext_lazy as _

from apps.managers import (ArchivedOrderManager, CancelledOrderManager,
                           ClientTransactionManager, DeliveredOrderManager,
                           DeliveryOrderManager, MissedCallOrderManager,
                           NewOrderManager, OperatorTransactionManager,
                           ReadyOrderManager, TransactionCancelledManager,
                           TransactionPaidManager, TransactionProcessManager)
from apps.models import Order, Transaction


class OrderHistoryProxyModel(Order):
    class Meta:
        proxy = True
        verbose_name = 'History Order'
        verbose_name_plural = _('History Orders')


class NewOrderProxyModel(Order):
    objects = NewOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'New Order'
        verbose_name_plural = _('New Orders')


class ReadyOrderProxyModel(Order):
    objects = ReadyOrderManager()

    class Meta:
        proxy = True
        verbose_name = ' Ready Order'
        verbose_name_plural = _('Ready Orders')


class DeliveryOrderProxyModel(Order):
    objects = DeliveryOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Delivery Order'
        verbose_name_plural = _('Delivery Orders')


class DeliveredOrderProxyModel(Order):
    objects = DeliveredOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Delivered Order'
        verbose_name_plural = _('Delivered Orders')


class CancelledOrderProxyModel(Order):
    objects = CancelledOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Cancelled Order'
        verbose_name_plural = _('Cancelled Orders')


class ArchivedOrderProxyModel(Order):
    objects = ArchivedOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Archived Order'
        verbose_name_plural = _('Archived Orders')


class MissedCallOrderProxyModel(Order):
    objects = MissedCallOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Missed Call Order'
        verbose_name_plural = _('Missed Call Orders')


class TransactionProcessProxyModel(Transaction):
    objects = TransactionProcessManager()

    class Meta:
        proxy = True
        verbose_name = 'Process Transaction'
        verbose_name_plural = _('Processes Transactions')


class TransactionPaidProxyModel(Transaction):
    objects = TransactionPaidManager()

    class Meta:
        proxy = True
        verbose_name = 'Paid Transaction'
        verbose_name_plural = _('Paid Transactions')


class TransactionCancelledProxyModel(Transaction):
    objects = TransactionCancelledManager()

    class Meta:
        proxy = True
        verbose_name = 'Cancelled Transaction'
        verbose_name_plural = _('Cancelled Transactions')


class OperatorTransactionProxyModel(Transaction):
    objects = OperatorTransactionManager()

    class Meta:
        proxy = True
        verbose_name = 'Operator Transaction'
        verbose_name_plural = _('Operator Transactions')


class ClientTransactionProxyModel(Transaction):
    objects = ClientTransactionManager()

    class Meta:
        proxy = True
        verbose_name = 'Client Transaction'
        verbose_name_plural = _('Client Transactions')
