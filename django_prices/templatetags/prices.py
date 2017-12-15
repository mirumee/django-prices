from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def amount(obj):
    result = '%s <span class="currency">%s</span>' % (obj.value, obj.currency)
    return mark_safe(result)


@register.filter
def discount_amount_for(discount, price):
    return discount.apply(price) - price
