from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def normalize_price(price, normalize):
    if normalize:
        normalized = price.normalize()
        if normalized.as_tuple().exponent >= 0:
            return normalized
    return price


@register.filter
def amount(obj, normalize=False):
    result = '%s <span class="currency">%s</span>' % (
        normalize_price(obj.value, normalize), obj.currency)
    return mark_safe(result)


@register.filter
def discount_amount_for(discount, price):
    return discount.apply(price) - price
