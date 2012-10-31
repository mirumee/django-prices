from django.db import models
from prices import Price

from . import forms


class PriceField(models.DecimalField):

    __metaclass__ = models.SubfieldBase
    description = "A field which stores a price."

    def __init__(self, verbose_name, currency, **kwargs):
        self.currency = currency
        super(PriceField, self).__init__(verbose_name, **kwargs)

    def to_python(self, value):
        if isinstance(value, Price):
            return value
        value = super(PriceField, self).to_python(value)
        if value is None:
            return value
        return Price(value, currency=self.currency)

    def get_prep_value(self, value):
        if value:
            value = value.net
        return super(PriceField, self).get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {'currency': self.currency,
                    'form_class': forms.PriceField}
        defaults.update(kwargs)
        return super(PriceField, self).formfield(**defaults)
