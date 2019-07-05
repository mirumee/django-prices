# coding: utf-8
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db.models.fields import DecimalField
from django_prices import forms, widgets, models
from prices import Money, TaxedMoney

from .models import Model, NullModel


def test_money_field_instance_init_by_money_object():
    instance = Model(price_net=Money(25, "USD"))
    assert instance.price.net.amount == 25


def test_taxed_money_field_instance_gross_and_net_are_set_separately():
    instance = Model(price_net=Money(25, "BTC"), price_gross=Money(30, "BTC"))
    assert instance.price == TaxedMoney(net=Money(25, "BTC"), gross=Money(30, "BTC"))


def test_money_field_instance_full_clean_raises_error_for_invalid_amount(db):
    model = Model(price_gross=Money("10.999", "BTC"))
    with pytest.raises(ValidationError):
        model.full_clean()


def test_taxed_money_field_set_instance_value():
    instance = Model()
    instance.price = TaxedMoney(Money(25, "BTC"), Money(30, "BTC"))
    assert instance.price_net == Money(25, "BTC")
    assert instance.price_gross == Money(30, "BTC")


def test_taxed_money_field_instance_init_by_taxed_money_object():
    instance = Model(price=TaxedMoney(Money(25, "BTC"), Money(30, "BTC")))
    assert instance.price_net == Money(25, "BTC")
    assert instance.price_gross == Money(30, "BTC")


def test_get_default_values():
    object_with_defaults = Model()
    net = Money(Model.DEFAULT_NET, Model.DEFAULT_CURRENCY)
    gross = Money(Model.DEFAULT_GROSS, Model.DEFAULT_CURRENCY)
    assert object_with_defaults.price_net == net
    assert object_with_defaults.price_net == gross
    assert object_with_defaults.price == TaxedMoney(net, gross)


def test_get_default_values_wth_nulls():
    object_with_defaults = NullModel()
    assert object_with_defaults.price_net is None
    assert object_with_defaults.price_net is None
    assert object_with_defaults.price is None


def test_money_field_instance_amount_and_currency_are_set_separately():
    instance = Model(price_net_amount=Decimal("10"), currency="USD")
    assert instance.price_net.amount == Decimal("10")
    assert instance.price_net.currency == "USD"
    assert instance.price_net == Money("10", "USD")


def test_money_field_set_instance_values():
    instance = Model()
    instance.price_net = Money(25, "USD")
    assert instance.price_net_amount == 25
    assert instance.currency == "USD"


def test_money_field_formfield_returns_form_with_select_input_if_choices_are_defined_for_currency_field():
    field = Model.price_net
    form_field = field.formfield()
    assert isinstance(form_field, forms.MoneyField)
    assert isinstance(form_field.widget, widgets.MoneyInput)


def test_money_field_init():
    field = models.MoneyField(amount_field="amount", currency_field="currency")
    assert field.get_default() == Money(0, None)
    assert field.amount_field == "amount"
    assert field.currency_field == "currency"


def test_compare_money_field_with_same_type_field():
    field_1 = models.MoneyField(
        amount_field="money_net_amount", currency_field="currency"
    )
    field_2 = models.MoneyField(
        amount_field="money_net_amount", currency_field="currency"
    )

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


def test_compare_money_field_with_django_field():
    field_1 = models.MoneyField(
        amount_field="money_net_amount", currency_field="currency"
    )
    field_2 = DecimalField(default="5", max_digits=9, decimal_places=2)

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    assert not field_1 > field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


def test_compare_money_field_with_taxed_money_field():
    field_1 = models.MoneyField(
        amount_field="money_net_amount", currency_field="currency"
    )
    field_2 = models.TaxedMoneyField(net_field="price_net", gross_field="price_gross")

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    assert not field_1 > field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


def test_taxed_money_field_init():
    field = models.TaxedMoneyField(
        net_amount_field="price_net",
        gross_amount_field="price_gross",
        currency="currency",
    )
    assert field.net_amount_field == "price_net"
    assert field.gross_amount_field == "price_gross"
    assert field.currency == "currency"


def test_compare_taxed_money_field_with_same_type_field():
    field_1 = models.TaxedMoneyField(
        net_amount_field="price_net",
        gross_amount_field="price_gross",
        currency="currency",
    )
    field_2 = models.TaxedMoneyField(
        net_amount_field="price_net",
        gross_amount_field="price_gross",
        currency="currency",
    )

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


def test_compare_taxed_money_field_with_django_field():
    field_1 = models.TaxedMoneyField(
        net_amount_field="price_net",
        gross_amount_field="price_gross",
        currency="currency",
    )
    field_2 = DecimalField(default="5", max_digits=9, decimal_places=2)

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    assert not field_1 > field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


def test_compare_taxed_money_field_with_money_field():
    field_1 = models.TaxedMoneyField(
        net_amount_field="price_net",
        gross_amount_field="price_gross",
        currency="currency",
    )
    field_2 = models.MoneyField(
        amount_field="money_net_amount", currency_field="currency"
    )

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    assert not field_1 > field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2
