from babel import support as babel_support
from babel import core as babel_core
from django import template
from django.conf import settings
from django.utils.translation import to_locale, get_language
try:
    from pytz import timezone
except ImportError:
    timezone = None

from ..utils.formatting import format_price


register = template.Library()


@register.filter
def amount(obj, format="text"):
    if format == "text":
        return format_price(obj.amount, obj.currency, html=False)
    if format == "html":
        return format_price(obj.amount, obj.currency, html=True)
    return _get_format().currency(obj.amount, obj.currency)


@register.filter
def discount_amount_for(discount, price):
    return discount(price) - price


def _get_format():
    locale = babel_core.Locale.parse(to_locale(get_language()))
    if timezone:
        tzinfo = timezone(settings.TIME_ZONE)
    else:
        tzinfo = None
    return babel_support.Format(locale, tzinfo)
