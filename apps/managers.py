from django.db.models import Manager

from users.models import User


class NewOrderManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.NEW)


class ReadyOrderManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.READY)


class DeliveryOrderManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.DELIVERY)


class DeliveredOrderManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.DELIVERED)


class CancelledOrderManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.CANCELLED)


class ArchivedOrderManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.ARCHIVED)


class MissedCallOrderManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.MISSED_CALL)


class TransactionProcessManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.PROCESS)


class TransactionCancelledManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.CANCELED)


class TransactionPaidManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.PAID)


class OperatorTransactionManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user__type=User.Type.OPERATOR)


class ClientTransactionManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user__type=User.Type.CLIENT)
