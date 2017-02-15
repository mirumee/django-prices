from __future__ import unicode_literals

from django import forms
from prices import Price

from .widgets import PriceInput

__all__ = ('PriceField', 'PriceInput')


class PriceField(forms.DecimalField):

    def __init__(self, currency, widget=PriceInput, *args, **kwargs):
        self.currency = currency
        if isinstance(widget, type):
            widget = widget(currency=self.currency, attrs={
                'type': 'number', 'step': 'any'})
        super(PriceField, self).__init__(*args, widget=widget, **kwargs)

    def to_python(self, value):
        value = super(PriceField, self).to_python(value)
        if value is None:
            return value
        return Price(value, currency=self.currency)

    def validate(self, value):
        if value is None:
            super(PriceField, self).validate(value)
        else:
            if not isinstance(value, Price):
                raise Exception('%r is not a valid price' % (value,))
            if value.currency != self.currency:
                raise forms.ValidationError(
                    'Invalid currency: %r (expected %r)' % (
                        value.currency, self.currency))
            super(PriceField, self).validate(value.net)

    def run_validators(self, value):
        if isinstance(value, Price):
            value = value.net
        return super(PriceField, self).run_validators(value)

    def has_changed(self, initial, data):
        if not isinstance(initial, Price):
            initial = self.to_python(initial)
        return super(PriceField, self).has_changed(initial, data)
