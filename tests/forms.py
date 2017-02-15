from django import forms
from django_prices.forms import PriceField

from . import models


class ModelForm(forms.ModelForm):
    class Meta:
        model = models.Model
        fields = ['price']


class RequiredPriceForm(forms.Form):
    price = PriceField(currency='BTC')


class OptionalPriceForm(forms.Form):
    price = PriceField(currency='BTC', required=False)
