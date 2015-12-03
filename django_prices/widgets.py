from __future__ import unicode_literals

from django import forms, VERSION as DJANGO_VERSION
from django.template.loader import render_to_string

from prices import Price

__all__ = ['PriceInput']


class PriceInput(forms.TextInput):
    template = 'prices/widget.html'
    input_type = 'number'

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
        widget = super(PriceInput, self).render(name, value, attrs=attrs)
        return render_to_string(self.template, {'widget': widget,
                                                'value': value,
                                                'currency': self.currency})
