from django import forms
from widgets import PriceInput
from prices import Price

__all__ = ('PriceField', 'PriceInput')


class PriceField(forms.DecimalField):

    def __init__(self, currency, widget=PriceInput, *args, **kwargs):
        self.currency = currency
        if isinstance(widget, type):
            widget = widget(currency=self.currency)
        self.widget = widget
        super(PriceField, self).__init__(*args, **kwargs)

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
