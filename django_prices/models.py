from django.db import models
from prices import Price

from . import forms


class PriceField(models.DecimalField):

    description = "A field which stores a price."

    def __init__(self, verbose_name, currency, **kwargs):
        self.currency = currency
        super(PriceField, self).__init__(verbose_name, **kwargs)

    def to_python(self, value):
        if isinstance(value, Price):
            return value
        return Price(value, currency=self.currency)

    def get_db_prep_save(self, value, connection):
        if isinstance(value, Price):
            value = value.net
        return super(PriceField, self).get_db_prep_save(value, connection)

    def formfield(self, **kwargs):
        defaults = {'currency': self.currency,
                    'form_class': forms.PriceField}
        defaults.update(kwargs)
        return super(PriceField, self).formfield(**defaults)

    def value_to_string(self, obj):
        val = self._get_val_from_obj(obj)
        return val.net
