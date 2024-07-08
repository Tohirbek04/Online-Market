import re

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm, Form
from django.utils.translation import gettext_lazy as _

from apps.models import Order, SiteSetting, Stream, Transaction


class OrderCreateModelForm(ModelForm):
    stream = ModelChoiceField(queryset=Stream.objects.all(), required=False)

    class Meta:
        model = Order
        fields = 'phone_number', 'name', 'product', 'stream'

    def clean_phone_number(self):
        phone_number = ''.join(re.findall(r'\d', self.cleaned_data.get('phone_number', )))
        return phone_number[3:]


class StreamCreateModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Stream
        fields = 'name', 'discount', 'product'

    def clean(self):
        product = self.cleaned_data.get('product')
        discount = self.cleaned_data.get('discount')

        if product.extra_balance and product.extra_balance < discount:
            messages.info(self.request, "you can't get much discount from extra balance.")
            raise ValidationError("you can't get much discount from extra balance.")
        return self.cleaned_data


class TransactionModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Transaction
        fields = 'card_number', 'amount'

    def clean(self):
        amount = self.cleaned_data['amount']
        min_sum = SiteSetting.objects.first().min_sum
        if amount >= self.request.user.balance:
            messages.info(self.request, _('not enough money !'))
            raise ValidationError("not enough money !")
        if amount < min_sum:
            messages.info(self.request, _(f"at least {min_sum} thousand can be solved !"))
            raise ValidationError(f"at least {min_sum} thousand can be solved !")
        return self.cleaned_data


class CourierForm(Form):
    pass
