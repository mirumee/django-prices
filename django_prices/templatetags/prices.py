from __future__ import unicode_literals

from django import template

register = template.Library()


def normalize_price(price, normalize):
    if normalize:
        return price.normalize()
    return price


@register.inclusion_tag('prices/price.html')
def gross(price, normalize=False):
    return {'amount': normalize_price(price.gross, normalize),
            'currency': price.currency}


@register.inclusion_tag('prices/price.html')
def net(price, normalize=False):
    return {'amount': normalize_price(price.net, normalize),
            'currency': price.currency}


@register.inclusion_tag('prices/price.html')
def tax(price, normalize=False):
    return {'amount': normalize_price(price.tax, normalize),
            'currency': price.currency}


@register.filter
def discount_amount_for(discount, price):
    return (price | discount) - price
