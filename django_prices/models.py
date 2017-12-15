from __future__ import unicode_literals

from django.db import models
from prices import Amount, Price

from . import forms


class AmountField(models.DecimalField):

    description = 'A field that stores an amount'

    def __init__(self, verbose_name=None, currency=None, **kwargs):
        self.currency = currency
        super(AmountField, self).__init__(verbose_name, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        if isinstance(value, Amount):
            if value.currency != self.currency:
                raise ValueError('Invalid currency: %r (expected %r)' % (
                    value.currency, self.currency))
            return value
        value = super(AmountField, self).to_python(value)
        if value is None:
            return value
        return Amount(value, self.currency)

    def run_validators(self, value):
        if isinstance(value, Amount):
            value = value.value
        return super(AmountField, self).run_validators(value)

    def get_prep_value(self, value):
        value = self.to_python(value)
        if value is not None:
            value = value.value
        return value

    def get_db_prep_save(self, value, connection):
        value = self.get_prep_value(value)
        db_value = connection.ops.adapt_decimalfield_value
        return db_value(value, self.max_digits, self.decimal_places)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        if value is not None:
            return value
        return super(AmountField, self).value_to_string(value)

    def formfield(self, **kwargs):
        defaults = {'currency': self.currency,
                    'form_class': forms.AmountField}
        defaults.update(kwargs)
        return super(AmountField, self).formfield(**defaults)

    def get_default(self):
        default = super(AmountField, self).get_default()
        return self.to_python(default)

    def deconstruct(self):
        name, path, args, kwargs = super(AmountField, self).deconstruct()
        kwargs['currency'] = self.currency
        return name, path, args, kwargs


class PriceField(object):

    description = 'A field that stores a price.'

    def __init__(self, net_field='price_net', gross_field='price_gross',
                 verbose_name=None, **kwargs):
        self.net_field = net_field
        self.gross_field = gross_field

    def __str__(self):
        return ('PriceField(net_field=%s, gross_field=%s)' %
                (self.net_field, self.gross_field))

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        net_val = getattr(instance, self.net_field)
        gross_val = getattr(instance, self.gross_field)
        return Price(net_val, gross_val)

    def __set__(self, instance, value):
        net = None
        gross = None
        if value is not None:
            net = value.net
            gross = value.gross
        setattr(instance, self.net_field, net)
        setattr(instance, self.gross_field, gross)
