from django.db import models
from prices import Price

from . import forms


class PriceField(models.DecimalField):

    __metaclass__ = models.SubfieldBase
    description = "A field which stores a price."

    def __init__(self, verbose_name=None, currency=None, **kwargs):
        self.currency = currency
        super(PriceField, self).__init__(verbose_name, **kwargs)

    def to_python(self, value):
        if isinstance(value, Price):
            return value
        value = super(PriceField, self).to_python(value)
        if value is None:
            return value
        return Price(value, currency=self.currency)

    def get_db_prep_save(self, value, connection):
        return connection.ops.value_to_db_decimal(value.net,
                                                  self.max_digits,
                                                  self.decimal_places)

    def get_prep_value(self, value):
        if value:
            value = value.net
        return super(PriceField, self).get_prep_value(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        if value:
            return value.net
        return super(PriceField, self).value_to_string(value)

    def formfield(self, **kwargs):
        defaults = {'currency': self.currency,
                    'form_class': forms.PriceField}
        defaults.update(kwargs)
        return super(PriceField, self).formfield(**defaults)

    def get_default(self):
        default = super(PriceField, self).get_default()
        return self.to_python(default)

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    rules = [
        ((PriceField,), [], {
            'currency': ('currency', {})
        }),
    ]
    add_introspection_rules(rules, ["^django_prices\.models"])
