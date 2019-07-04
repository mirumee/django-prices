import re
from decimal import Decimal, InvalidOperation

from babel.core import get_global
from babel.numbers import format_currency
from django import template
from django.utils.safestring import mark_safe

from django_babel.templatetags.babel import currencyfmt

from ..locale_utils import get_locale_data

register = template.Library()


def get_currency_fraction(currency):
    fractions = get_global("currency_fractions")
    try:
        fraction = fractions[currency]
    except KeyError:
        fraction = fractions["DEFAULT"]
    return fraction[0]


def format_price(value, currency, html=False):
    """
    Format decimal value as currency
    """
    try:
        value = Decimal(value)
    except (TypeError, InvalidOperation):
        return ""

    locale, locale_code = get_locale_data()
    pattern = locale.currency_formats.get("standard").pattern

    if html:
        pattern = re.sub("(\xa4+)", '<span class="currency">\\1</span>', pattern)

    result = format_currency(value, currency, format=pattern, locale=locale_code)
    return mark_safe(result)


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
