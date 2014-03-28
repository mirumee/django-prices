from babeldjango.templatetags.babel import currencyfmt
from django import template

register = template.Library()


@register.simple_tag
def gross(price):
    return currencyfmt(price.gross, price.currency)


@register.simple_tag
def net(price):
    return currencyfmt(price.net, price.currency)


@register.simple_tag
def tax(price):
    return currencyfmt(price.tax, price.currency)
