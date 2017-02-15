from __future__ import unicode_literals

from django import template

register = template.Library()


@register.inclusion_tag('prices/price.html')
def gross(price):
    return {'amount': price.gross, 'currency': price.currency}


@register.inclusion_tag('prices/price.html')
def net(price):
    return {'amount': price.net, 'currency': price.currency}


@register.inclusion_tag('prices/price.html')
def tax(price):
    return {'amount': price.tax, 'currency': price.currency}


@register.filter
def discount_amount_for(discount, price):
    return (price | discount) - price
