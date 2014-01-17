from __future__ import unicode_literals

from django import forms, VERSION as DJANGO_VERSION
from django.utils.html import escape
from django.utils.safestring import mark_safe

from prices import Price

__all__ = ['PriceInput']


class PriceInput(forms.TextInput):

    def __init__(self, currency, *args, **kwargs):
        self.currency = currency
        super(PriceInput, self).__init__(*args, **kwargs)

    def _format_value(self, value):
        if isinstance(value, Price):
            value = value.net
        return value

    if DJANGO_VERSION < (1, 6):
        def _has_changed(self, initial, data):
            if isinstance(initial, Price):
                initial = initial.net
            return super(PriceInput, self)._has_changed(initial, data)

    def render(self, name, value, attrs=None):
        result = super(PriceInput, self).render(name, value)
        result += ' %s' % (escape(self.currency),)
        return mark_safe(result)
