from django import forms
from prices import Money

from django_prices.forms import MoneyField
from django_prices.validators import MaxMoneyValidator, MinMoneyValidator

from . import models

AVAILABLE_CURRENCIES = ["BTC", "USD"]


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


class FixedCurrencyRequiredPriceForm(forms.Form):
    price = MoneyField(available_currencies=["BTC"])


class FixedCurrencyOptionalPriceForm(forms.Form):
    price = MoneyField(available_currencies=["BTC"], required=False)


class ValidatedPriceForm(forms.Form):
    price = MoneyField(
        available_currencies=AVAILABLE_CURRENCIES,
        max_digits=9,
        decimal_places=2,
        validators=[
            MinMoneyValidator(Money(5, "USD")),
            MaxMoneyValidator(Money(15, "USD")),
        ],
    )


class MaxMinPriceForm(forms.Form):
    price = MoneyField(
        available_currencies=AVAILABLE_CURRENCIES,
        min_values=[Money(5, "USD"), Money(6, "BTC")],
        max_values=[Money(15, "USD"), Money(16, "BTC")],
    )
