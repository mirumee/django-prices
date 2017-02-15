from django.db import models
from django_prices.models import PriceField


class Model(models.Model):
    price = PriceField(currency='BTC', default='5', max_digits=9,
                       decimal_places=2)
