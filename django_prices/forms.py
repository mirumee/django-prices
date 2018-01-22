from django import forms
from prices import Money

from .widgets import MoneyInput

__all__ = ('MoneyField', 'MoneyInput')


class MoneyField(forms.DecimalField):
    def __init__(self, currency, widget=MoneyInput, *args, **kwargs):
        self.currency = currency
        if isinstance(widget, type):
            widget = widget(currency=self.currency, attrs={
                'type': 'number', 'step': 'any'})
        super(MoneyField, self).__init__(*args, widget=widget, **kwargs)

    def to_python(self, value):
        value = super(MoneyField, self).to_python(value)
        if value is None:
            return value
        return Money(value, self.currency)

    def validate(self, value):
        if value is None:
            super(MoneyField, self).validate(value)
        else:
            if not isinstance(value, Money):
                raise Exception('%r is not a valid price' % (value,))
            if value.currency != self.currency:
                raise forms.ValidationError(
                    'Invalid currency: %r (expected %r)' % (
                        value.currency, self.currency))
            super(MoneyField, self).validate(value.amount)

    def run_validators(self, value):
        if isinstance(value, Money):
            value = value.amount
        return super(MoneyField, self).run_validators(value)

    def has_changed(self, initial, data):
        if not isinstance(initial, Money):
            initial = self.to_python(initial)
        return super(MoneyField, self).has_changed(initial, data)
