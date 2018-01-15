from __future__ import unicode_literals

from django import forms
from django.template.loader import render_to_string
from prices import Price

__all__ = ['PriceInput']


class PriceInput(forms.TextInput):
    template = 'prices/widget.html'
    input_type = 'number'

    def __init__(self, currency, *args, **kwargs):
        self.currency = currency
        super(PriceInput, self).__init__(*args, **kwargs)

    def format_value(self, value):
        if not value:
            return value
        if isinstance(value, Price):
            value = value.net.value
        if isinstance(value, Amount):
            value = value.value
        else:
            value = value
        return value

    def render(self, name, value, attrs=None):
        widget = super(PriceInput, self).render(name, value, attrs=attrs)
        return render_to_string(self.template, {'widget': widget,
                                                'value': value,
                                                'currency': self.currency})
