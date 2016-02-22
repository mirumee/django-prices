from decimal import Decimal, InvalidOperation
import re

from babel.core import Locale, UnknownLocaleError
from babel.numbers import format_currency
from babeldjango.templatetags.babel import currencyfmt
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, to_locale


register = template.Library()


def format_price(value, currency):
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
    pattern = re.sub(
        '(\xa4+)', '<span class="currency">\\1</span>', pattern)
    result = format_currency(value, currency, pattern, locale=locale_code)
    return mark_safe(result)


@register.simple_tag
def gross(price, html=False):
    if html:
        return format_price(price.gross, price.currency)
    return currencyfmt(price.gross, price.currency)


@register.simple_tag
def net(price, html=False):
    if html:
        return format_price(price.net, price.currency)
    return currencyfmt(price.net, price.currency)


@register.simple_tag
def tax(price, html=False):
    if html:
        return format_price(price.tax, price.currency)
    return currencyfmt(price.tax, price.currency)
