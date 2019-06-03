from django.db import models
from django_prices.models import MoneyCurrencyField, MoneyField, TaxedMoneyField


class Model(models.Model):
    price_net = MoneyField(
        "net", currency="BTC", default="5", max_digits=9, decimal_places=2
    )
    price_gross = MoneyField(
        "gross", currency="BTC", default="5", max_digits=9, decimal_places=2
    )
    price = TaxedMoneyField(net_field="price_net", gross_field="price_gross")


class CurrencyModel(models.Model):
    currency = models.CharField(max_length=3, default="BTC")
    money_net_amount = models.DecimalField(max_digits=9, decimal_places=2)
    money_net = MoneyCurrencyField(
        amount_field="money_net_amount", currency_field="currency"
    )
    money_gross_amount = models.DecimalField(max_digits=9, decimal_places=2)
    money_gross = MoneyCurrencyField(
        amount_field="money_gross_amount", currency_field="currency"
    )
    taxed_money = TaxedMoneyField(net_field="money_net", gross_field="money_gross")
