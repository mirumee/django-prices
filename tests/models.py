from django.db import models
from django_prices.models import AmountField, PriceField


class Model(models.Model):
    price_net = AmountField(
        'price_net', currency='BTC', default='5', max_digits=9,
        decimal_places=2)
    price_gross = AmountField(
        'price_gross', currency='BTC', default='5', max_digits=9,
        decimal_places=2)
    price = PriceField(net_field='price_net', gross_field='price_gross')
