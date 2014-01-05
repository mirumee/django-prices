from babel.numbers import format_currency
from django import template
from django.utils import translation

register = template.Library()
language = translation.get_language()
locale = translation.to_locale(language)

@register.simple_tag
def gross(price):
    return format_currency(price.gross, price.currency, locale=locale)


@register.simple_tag
def net(price):
    return format_currency(price.net, price.currency, locale=locale)


@register.simple_tag
def tax(price):
    return format_currency(price.tax, price.currency, locale=locale)
