from django.db.models import Manager


class ProductCountManager(Manager):
    def all(self):
        return self.filter(count__gt=0)
