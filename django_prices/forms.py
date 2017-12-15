from __future__ import unicode_literals

from django import forms
from prices import Amount, Price

from .widgets import PriceInput

__all__ = ('PriceField', 'PriceInput')


class AmountField(forms.DecimalField):
    def __init__(self, currency, widget=PriceInput, *args, **kwargs):
        self.currency = currency
        if isinstance(widget, type):
            widget = widget(currency=self.currency, attrs={
                'type': 'number', 'step': 'any'})
        super(AmountField, self).__init__(*args, widget=widget, **kwargs)

    def to_python(self, value):
        value = super(AmountField, self).to_python(value)
        if value is None:
            return value
        return Amount(value, self.currency)

    def validate(self, value):
        if value is None:
            super(AmountField, self).validate(value)
        else:
            if not isinstance(value, Amount):
                raise Exception('%r is not a valid price' % (value,))
            if value.currency != self.currency:
                raise forms.ValidationError(
                    'Invalid currency: %r (expected %r)' % (
                        value.currency, self.currency))
            super(AmountField, self).validate(value.value)

    def run_validators(self, value):
        if isinstance(value, Amount):
            value = value.value
        return super(AmountField, self).run_validators(value)

    def has_changed(self, initial, data):
        if not isinstance(initial, Amount):
            initial = self.to_python(initial)
        return super(AmountField, self).has_changed(initial, data)
