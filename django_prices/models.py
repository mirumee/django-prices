from django.db import models
from django.conf import settings
from prices import Price

from . import forms


BaseField = models.SubfieldBase('BaseField', (models.DecimalField,), {})


class PriceField(BaseField):

    description = 'A field which stores a price.'

    def __init__(self, verbose_name=None, currency=None, **kwargs):
        self.currency = currency
        super(PriceField, self).__init__(verbose_name, **kwargs)

    def to_python(self, value):
        if isinstance(value, Price):
            if value.currency != self.currency:
                raise ValueError('Invalid currency: %r (expected %r)' % (
                    value.currency, self.currency))
            return value
        value = super(PriceField, self).to_python(value)
        if value is None:
            return value
        return Price(value, currency=self.currency)

    def get_prep_value(self, value):
        value = self.to_python(value)
        if value is not None:
            value = value.net
        return value

    def get_db_prep_save(self, value, connection):
        value = self.get_prep_value(value)
        return connection.ops.value_to_db_decimal(value,
                                                  self.max_digits,
                                                  self.decimal_places)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        if value is not None:
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

    def deconstruct(self):
        name, path, args, kwargs = super(PriceField, self).deconstruct()
        kwargs['currency'] = self.currency
        return name, path, args, kwargs

if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    rules = [
        ((PriceField,), [], {
            'currency': ('currency', {})
        })
    ]
    add_introspection_rules(rules, ['^django_prices\.models'])
