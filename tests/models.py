from django.db import models
from django_prices.models import MoneyField, TaxedMoneyField


class Model(models.Model):
    price_net = MoneyField(
        "net", currency="BTC", default="5", max_digits=9, decimal_places=2
    )
    price_gross = MoneyField(
        "gross", currency="BTC", default="5", max_digits=9, decimal_places=2
    )
    price = TaxedMoneyField(net_field="price_net", gross_field="price_gross")
