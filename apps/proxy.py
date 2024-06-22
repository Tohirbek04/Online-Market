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
        verbose_name = 'Order History'
        verbose_name_plural = 'Order Histories'


class NewOrderProxyModel(Order):
    objects = NewOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Order New'
        verbose_name_plural = 'Order News'


class ReadyOrderProxyModel(Order):
    objects = ReadyOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Order Ready'
        verbose_name_plural = 'Order Ready'


class DeliveryOrderProxyModel(Order):
    objects = DeliveryOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Order Delivery'
        verbose_name_plural = 'Order Delivery'


class DeliveredOrderProxyModel(Order):
    objects = DeliveredOrderManager()

    class Meta:
        proxy = True
        verbose_name = _('Order Delivered')


class CancelledOrderProxyModel(Order):
    objects = CancelledOrderManager()

    class Meta:
        proxy = True
        verbose_name = _('Order Cancelled')


class ArchivedOrderProxyModel(Order):
    objects = ArchivedOrderManager()

    class Meta:
        proxy = True
        verbose_name = _('Order Archived')


class MissedCallOrderProxyModel(Order):
    objects = MissedCallOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Order MissedCall'
        verbose_name_plural = _('Order MissedCalls')


class TransactionProcessProxyModel(Transaction):
    objects = TransactionProcessManager()

    class Meta:
        proxy = True
        verbose_name = 'Transaction Process'
        verbose_name_plural = 'Transaction Processes'


class TransactionPaidProxyModel(Transaction):
    objects = TransactionPaidManager()

    class Meta:
        proxy = True
        verbose_name = 'Transaction Paid'


class TransactionCancelledProxyModel(Transaction):
    objects = TransactionCancelledManager()

    class Meta:
        proxy = True
        verbose_name = 'Transaction Cancelled'


class OperatorTransactionProxyModel(Transaction):
    objects = OperatorTransactionManager()

    class Meta:
        proxy = True
        verbose_name = 'Transaction Operator'



class ClientTransactionProxyModel(Transaction):
    objects = ClientTransactionManager()

    class Meta:
        proxy = True
        verbose_name = 'Transaction Client'
