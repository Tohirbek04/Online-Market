from django.db.models import Manager


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
