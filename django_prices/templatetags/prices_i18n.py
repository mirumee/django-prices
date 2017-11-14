from __future__ import unicode_literals

import re
from decimal import Decimal, InvalidOperation

from babel.core import Locale, UnknownLocaleError, get_global
from babel.numbers import format_currency
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, to_locale

from django_babel.templatetags.babel import currencyfmt

register = template.Library()


def get_currency_fraction(currency):
    fractions = get_global('currency_fractions')
    try:
        fraction = fractions[currency]
    except KeyError:
        fraction = fractions['DEFAULT']
    return fraction[0]


def change_pattern(pattern, currency, normalize):
    fractions = get_currency_fraction(currency)
    replacement = '#' if normalize else '0'
    return pattern.replace('.00', '.' + replacement * fractions)


def format_price(value, currency, html=False, normalize=False):
    """
    Format decimal value as currency
    """
    try:
        value = Decimal(value)
    except (TypeError, InvalidOperation):
        return ''
    language = get_language()
    if not language:
        language = settings.LANGUAGE_CODE
    locale_code = to_locale(language)
    locale = None
    try:
        locale = Locale.parse(locale_code)
    except (ValueError, UnknownLocaleError):
        # Invalid format or unknown locale
        # Fallback to the default language
        language = settings.LANGUAGE_CODE
        locale_code = to_locale(language)
        locale = Locale.parse(locale_code)
    currency_format = locale.currency_formats.get('standard')
    pattern = currency_format.pattern
    if value.normalize().as_tuple().exponent < 0:
        normalize = False
    pattern = change_pattern(pattern, currency, normalize)

    if html:
        pattern = re.sub(
            '(\xa4+)', '<span class="currency">\\1</span>', pattern)
    result = format_currency(
        value, currency, pattern, locale=locale_code,
        currency_digits=(not normalize))
    return mark_safe(result)


@register.simple_tag
def gross(price, html=False, normalize=False):
    if html or normalize:
        return format_price(price.gross, price.currency, html, normalize)
    return currencyfmt(price.gross, price.currency)


@register.simple_tag
def net(price, html=False, normalize=False):
    if html or normalize:
        return format_price(price.net, price.currency, html, normalize)
    return currencyfmt(price.net, price.currency)


@register.simple_tag
def tax(price, html=False, normalize=False):
    if html or normalize:
        return format_price(price.tax, price.currency, html, normalize)
    return currencyfmt(price.tax, price.currency)
