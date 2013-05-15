from babel.numbers import format_currency
from django import template

register = template.Library()


@register.simple_tag
def gross(price):
    return format_currency(price.gross, price.currency)


@register.simple_tag
def net(price):
    return format_currency(price.net, price.currency)


@register.simple_tag
def tax(price):
    return format_currency(price.tax, price.currency)
