from django.db import models
from django_prices.models import MoneyField, TaxedMoneyField

AVAILABLE_CURRENCIES = [("BTC", "bitcoins"), ("USD", "US dollar")]


class Model(models.Model):
    DEFAULT_NET = "5"
    DEFAULT_GROSS = "5"
    DEFAULT_CURRENCY = "BTC"

    currency = models.CharField(
        max_length=3, default=DEFAULT_CURRENCY, choices=AVAILABLE_CURRENCIES
    )
    price_net_amount = models.DecimalField(
        max_digits=9, decimal_places=2, default=DEFAULT_NET
    )
    price_net = MoneyField(amount_field="price_net_amount", currency_field="currency")
    price_gross_amount = models.DecimalField(
        max_digits=9, decimal_places=2, default=DEFAULT_GROSS
    )
    price_gross = MoneyField(
        amount_field="price_gross_amount", currency_field="currency"
    )
    price = TaxedMoneyField(
        net_amount_field="price_net_amount",
        gross_amount_field="price_gross_amount",
        currency="currency",
    )


class NullModel(models.Model):
    DEFAULT_CURRENCY = "BTC"

    currency = models.CharField(
        max_length=3, default=DEFAULT_CURRENCY, choices=AVAILABLE_CURRENCIES
    )
    price_net_amount = models.DecimalField(
        max_digits=9, decimal_places=2, default=None, null=True
    )
    price_net = MoneyField(amount_field="price_net_amount", currency_field="currency")
    price_gross_amount = models.DecimalField(
        max_digits=9, decimal_places=2, default=None, null=True
    )
    price_gross = MoneyField(
        amount_field="price_gross_amount", currency_field="currency"
    )
    price = TaxedMoneyField(
        net_amount_field="price_net_amount",
        gross_amount_field="price_gross_amount",
        currency="currency",
    )
