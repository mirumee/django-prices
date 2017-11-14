from __future__ import unicode_literals

from django.db import models
from prices import Price

from . import forms


class Creator(object):
    """
    A placeholder class that provides a way to set the attribute on the model.
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__[self.field.name]

    def __set__(self, obj, value):
        if isinstance(value, models.Expression):
            obj.__dict__[self.field.name] = value
        else:
            obj.__dict__[self.field.name] = self.field.to_python(value)


class PriceField(models.DecimalField):

    description = 'A field that stores a price.'

    def __init__(self, verbose_name=None, currency=None, **kwargs):
        self.currency = currency
        super(PriceField, self).__init__(verbose_name, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        super(PriceField, self).contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, Creator(self))

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

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

    def run_validators(self, value):
        if isinstance(value, Price):
            value = value.net
        return super(PriceField, self).run_validators(value)

    def get_prep_value(self, value):
        value = self.to_python(value)
        if value is not None:
            value = value.net
        return value

    def get_db_prep_save(self, value, connection):
        value = self.get_prep_value(value)
        db_value = connection.ops.adapt_decimalfield_value
        return db_value(value, self.max_digits, self.decimal_places)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
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
