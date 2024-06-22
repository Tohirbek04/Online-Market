from django.template import Library

register = Library()


@register.filter()
def card_number(number):
    return f"{number[:4]} * * * * * {number[-4:]}"
