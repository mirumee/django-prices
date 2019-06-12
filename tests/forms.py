from django import forms
from prices import Money

from django_prices.forms import MoneyField
from django_prices.validators import MaxMoneyValidator, MinMoneyValidator

from . import models


class ModelForm(forms.ModelForm):
    class Meta:
        model = models.Model
        fields = []

    price_net = MoneyField(default_currency="BTC")
    price_gross = MoneyField(default_currency="BTC")


class RequiredPriceForm(forms.Form):
    price_net = MoneyField(default_currency="BTC")


class OptionalPriceForm(forms.Form):
    price_net = MoneyField(default_currency="BTC", required=False)


class ValidatedPriceForm(forms.Form):
    price = MoneyField(
        default_currency="USD",
        max_digits=9,
        decimal_places=2,
        validators=[
            MinMoneyValidator(Money(5, currency="USD")),
            MaxMoneyValidator(Money(15, currency="USD")),
        ],
    )
