import itertools

from django.db import models
from django.utils.functional import cached_property
from prices import Money, TaxedMoney

from . import forms
from .validators import MoneyPrecisionValidator


class MoneyField(models.DecimalField):

    description = 'A field that stores an amount of money'

    def __init__(self, verbose_name=None, currency=None, **kwargs):
        self.currency = currency
        super(MoneyField, self).__init__(verbose_name, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        if isinstance(value, Money):
            if value.currency != self.currency:
                raise ValueError('Invalid currency: %r (expected %r)' % (
                    value.currency, self.currency))
            return value
        value = super(MoneyField, self).to_python(value)
        if value is None:
            return value
        return Money(value, self.currency)

    def get_prep_value(self, value):
        value = self.to_python(value)
        if value is not None:
            return value.amount
        return value

    def get_db_prep_save(self, value, connection):
        value = self.get_prep_value(value)
        db_value = connection.ops.adapt_decimalfield_value
        return db_value(value, self.max_digits, self.decimal_places)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        if value is not None:
            return value
        return super(MoneyField, self).value_to_string(value)

    def formfield(self, **kwargs):
        defaults = {'currency': self.currency,
                    'form_class': forms.MoneyField}
        defaults.update(kwargs)
        return super(MoneyField, self).formfield(**defaults)

    def get_default(self):
        default = super(MoneyField, self).get_default()
        return self.to_python(default)

    @cached_property
    def validators(self):
        validators = list(
            itertools.chain(self.default_validators, self._validators))
        return validators + [MoneyPrecisionValidator(
                self.currency, self.max_digits, self.decimal_places)]

    def deconstruct(self):
        name, path, args, kwargs = super(MoneyField, self).deconstruct()
        kwargs['currency'] = self.currency
        return name, path, args, kwargs


class TaxedMoneyField(object):

    description = 'A field that stores a price.'

    def __init__(self, net_field='price_net', gross_field='price_gross',
                 verbose_name=None, **kwargs):
        self.net_field = net_field
        self.gross_field = gross_field

    def __str__(self):
        return ('TaxedMoneyField(net_field=%s, gross_field=%s)' %
                (self.net_field, self.gross_field))

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        net_val = getattr(instance, self.net_field)
        gross_val = getattr(instance, self.gross_field)
        return TaxedMoney(net_val, gross_val)

    def __set__(self, instance, value):
        net = None
        gross = None
        if value is not None:
            net = value.net
            gross = value.gross
        setattr(instance, self.net_field, net)
        setattr(instance, self.gross_field, gross)
