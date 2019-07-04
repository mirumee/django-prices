import warnings

from django import template

from .prices import amount as new_amount
from ..utils.formatting import (
    format_price as new_format_price,
    get_currency_fraction as new_get_currency_fraction,
)

register = template.Library()


def deprecation_warning():
    warnings.warn(
        "Module `prices_i18n` is deprecated and will be removed in future version. Use `prices` instead."
    )


def get_currency_fraction(currency):
    deprecation_warning()
    return new_get_currency_fraction(currency)


def format_price(value, currency, html=False):
    deprecation_warning()
    return new_format_price(value, currency, html)


@register.filter
def amount(obj, format="text"):
    deprecation_warning()
    return new_amount(obj, format)
