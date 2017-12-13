from __future__ import unicode_literals

from django import template

register = template.Library()


def normalize_price(price, normalize):
    if normalize:
        normalized = price.normalize()
        if normalized.as_tuple().exponent >= 0:
            return normalized
    return price


@register.filter()
def amount(obj, normalize=False):
    return '%s <span class="currency">%s</span>' % (
        normalize_price(obj.value, normalize), obj.currency)


@register.inclusion_tag('prices/price.html')
def gross(price, normalize=False):
    return {'amount': normalize_price(price.gross.value, normalize),
            'currency': price.currency}


@register.inclusion_tag('prices/price.html')
def net(price, normalize=False):
    return {'amount': normalize_price(price.net.value, normalize),
            'currency': price.currency}


@register.inclusion_tag('prices/price.html')
def tax(price, normalize=False):
    return {'amount': normalize_price(price.tax.value, normalize),
            'currency': price.currency}


@register.filter
def discount_amount_for(discount, price):
    return discount.apply(price) - price
