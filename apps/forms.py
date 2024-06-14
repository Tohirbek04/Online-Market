import re

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from apps.models import Order, Stream


class OrderCreateModelForm(ModelForm):
    class Meta:
        model = Order
        fields = 'phone_number', 'name', 'product'

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', )
        phone_number = ''.join(re.findall(r'\d', phone))
        return phone_number[3:]


class StreamCreateModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")  # Need to pop here as well, even if you don't need it
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
