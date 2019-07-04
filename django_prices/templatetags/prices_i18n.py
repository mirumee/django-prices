import warnings

from django import template

from .prices import get_currency_fraction, format_price, amount

register = template.Library()


def deprecation_warning():
    warnings.warn(
        "Use tags from module `prices`. Module `prices_i18n` is going to be deprecated."
    )


def get_currency_fraction(currency):
    deprecation_warning()
    return get_currency_fraction(currency)


def format_price(value, currency, html=False):
    deprecation_warning()
    return format_price(value, currency, html)


@register.filter
def amount(obj, format="text"):
    deprecation_warning()
    return amount(obj, format)
