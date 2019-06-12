import itertools
from decimal import Decimal

from django.core import validators
from django.db import models
from django.db.models import Field
from django.utils.functional import cached_property
from prices import Money, TaxedMoney

from . import forms
from .validators import MoneyPrecisionValidator


class MoneyField:

    description = (
        "A field that combines an amount of money and currency code into Money"
        "It allows to store prices with different currencies in one database."
    )
    empty_values = list(validators.EMPTY_VALUES)

    # Field flags
    auto_created = False
    blank = True
    concrete = False
    editable = False

    is_relation = False
    remote_field = None

    def __init__(
        self,
        amount_field="price_amount",
        currency_field="price_currency",
        verbose_name=None,
        **kwargs
    ):
        self.amount_field = amount_field
        self.currency_field = currency_field

        self.column = None
        self.primary_key = False

        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def __str__(self):
        return "MoneyField(amount_field=%s, currency_field=%s)" % (
            self.amount_field,
            self.currency_field,
        )

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        amount = getattr(instance, self.amount_field)
        currency = getattr(instance, self.currency_field)
        if amount and currency:
            return Money(amount, currency)
        return self.get_default()

    def __hash__(self):
        return hash(self.creation_counter)

    def __set__(self, instance, value):
        amount = None
        currency = None
        if value is not None:
            amount = value.amount
            currency = value.currency
        setattr(instance, self.amount_field, amount)
        setattr(instance, self.currency_field, currency)

    def __eq__(self, other):
        if isinstance(other, (Field, MoneyField, TaxedMoneyField)):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (Field, MoneyField, TaxedMoneyField)):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def contribute_to_class(self, cls, name, **kwargs):
        self.attname = self.name = name
        self.model = cls
        cls._meta.add_field(self, private=True)
        setattr(cls, name, self)

    def clean(self, value, model_instance):
        # Shortcircut clean() because Django calls it on all fields with
        # is_relation = False
        return value

    def formfield(self, **kwargs):
        currency = ""
        if hasattr(self, "model"):
            currency = self.model._meta.get_field(self.currency_field).get_default()
        return forms.MoneyField(default_currency=currency)

    def get_default(self):
        default_currency = ""
        default_amount = Decimal(0)
        if hasattr(self, "model"):
            default_currency = self.model._meta.get_field(
                self.currency_field
            ).get_default()
            d = self.model._meta.get_field(self.amount_field).get_default()
            default_amount = self.model._meta.get_field(self.amount_field).to_python(d)

        return Money(default_amount, default_currency)


class TaxedMoneyField(object):

    description = "A field that combines net and gross fields values into TaxedMoney."
    empty_values = list(validators.EMPTY_VALUES)

    # Field flags
    auto_created = False
    blank = True
    concrete = False
    editable = False

    is_relation = False
    remote_field = None

    def __init__(
        self,
        net_field="price_net",
        gross_field="price_gross",
        verbose_name=None,
        **kwargs
    ):
        self.net_field = net_field
        self.gross_field = gross_field

        self.column = None
        self.primary_key = False

        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def __str__(self):
        return "TaxedMoneyField(net_field=%s, gross_field=%s)" % (
            self.net_field,
            self.gross_field,
        )

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        net_val = getattr(instance, self.net_field)
        gross_val = getattr(instance, self.gross_field)
        return TaxedMoney(net_val, gross_val)

    def __hash__(self):
        return hash(self.creation_counter)

    def __set__(self, instance, value):
        net = None
        gross = None
        if value is not None:
            net = value.net
            gross = value.gross
        setattr(instance, self.net_field, net)
        setattr(instance, self.gross_field, gross)

    def __eq__(self, other):
        if isinstance(other, (Field, MoneyField, TaxedMoneyField)):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (Field, MoneyField, TaxedMoneyField)):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def contribute_to_class(self, cls, name, **kwargs):
        self.attname = self.name = name
        self.model = cls
        cls._meta.add_field(self, private=True)
        setattr(cls, name, self)

    def clean(self, value, model_instance):
        # Shortcircut clean() because Django calls it on all fields with
        # is_relation = False, but we rely on our net and gross fields for
        # actual validation.
        return value
