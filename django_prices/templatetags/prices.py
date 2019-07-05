from django import template

from django_babel.templatetags.babel import currencyfmt

from ..utils.formatting import format_price


register = template.Library()


@register.filter
def amount(obj, format="text"):
    if format == "text":
        return format_price(obj.amount, obj.currency, html=False)
    if format == "html":
        return format_price(obj.amount, obj.currency, html=True)
    return currencyfmt(obj.amount, obj.currency)


@register.filter
def discount_amount_for(discount, price):
    return discount(price) - price
