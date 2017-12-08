from django import forms
from django_prices.forms import PriceField
from django_prices.models import AmountField

from . import models


class ModelForm(forms.ModelForm):
    class Meta:
        model = models.Model
        fields = ['price_net', 'price_gross']


class RequiredPriceForm(forms.Form):
    price = PriceField(currency='BTC')


class OptionalPriceForm(forms.Form):
    price = PriceField(currency='BTC', required=False)
