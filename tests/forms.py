from django import forms
from prices import Money

from django_prices.forms import MoneyField
from django_prices.validators import MaxMoneyValidator, MinMoneyValidator

from . import models

AVAILABLE_CURRENCIES = [("BTC", "bitcoins"), ("USD", "US dollar")]


class ModelForm(forms.ModelForm):
    class Meta:
        model = models.Model
        fields = []

    price_net = MoneyField(available_currencies=AVAILABLE_CURRENCIES)
    price_gross = MoneyField(available_currencies=AVAILABLE_CURRENCIES)


class RequiredPriceForm(forms.Form):
    price_net = MoneyField(available_currencies=AVAILABLE_CURRENCIES)


class OptionalPriceForm(forms.Form):
    price_net = MoneyField(available_currencies=AVAILABLE_CURRENCIES, required=False)


class ValidatedPriceForm(forms.Form):
    price = MoneyField(
        available_currencies=AVAILABLE_CURRENCIES,
        max_digits=9,
        decimal_places=2,
        validators=[
            MinMoneyValidator(Money(5, currency="USD")),
            MaxMoneyValidator(Money(15, currency="USD")),
        ],
    )


class MaxMinPriceForm(forms.Form):
    price = MoneyField(
        available_currencies=AVAILABLE_CURRENCIES,
        min_values=[Money(5, currency="USD"), Money(6, currency="BTC")],
        max_values=[Money(15, currency="USD"), Money(16, currency="BTC")],
    )
