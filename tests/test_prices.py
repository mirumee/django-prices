# coding: utf-8
from __future__ import unicode_literals

import functools
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import connection
from django.utils import translation
from django_prices import forms, widgets
from django_prices.models import MoneyCurrencyField, MoneyField, TaxedMoneyField
from django_prices.templatetags import prices, prices_i18n
from django_prices.validators import (
    MaxMoneyValidator,
    MinMoneyValidator,
    MoneyPrecisionValidator,
)
from prices import Money, TaxedMoney, percentage_discount

from .forms import ModelForm, OptionalPriceForm, RequiredPriceForm, ValidatedPriceForm
from .models import CurrencyModel, Model


@pytest.fixture(scope="module")
def money_fixture():
    return Money("10", "USD")


@pytest.fixture(scope="module")
def money_with_decimals():
    return Money("10.20", "USD")


@pytest.fixture(scope="module")
def price_fixture():
    return TaxedMoney(net=Money("10", "USD"), gross=Money("15", "USD"))


@pytest.fixture(scope="module")
def price_with_decimals():
    return TaxedMoney(net=Money("10.20", "USD"), gross=Money("15", "USD"))


def test_money_field_init():
    field = MoneyField(currency="BTC", default="5", max_digits=9, decimal_places=2)
    assert field.get_default() == Money(5, "BTC")


def test_money_field_get_prep_value():
    field = MoneyField(
        "price", currency="BTC", default="5", max_digits=9, decimal_places=2
    )
    assert field.get_prep_value(Money(5, "BTC")) == Decimal(5)


def test_money_field_get_db_prep_save():
    field = MoneyField(
        "price", currency="BTC", default="5", max_digits=9, decimal_places=2
    )
    value = field.get_db_prep_save(Money(5, "BTC"), connection)
    assert value == "5.00"


def test_money_field_value_to_string():
    instance = Model(price_net=30)
    field = instance._meta.get_field("price_net")
    assert field.value_to_string(instance) == Decimal("30")


def test_money_field_from_db_value():
    field = MoneyField(
        "price", currency="BTC", default="5", max_digits=9, decimal_places=2
    )
    assert field.from_db_value(7, None, None, None) == Money(7, "BTC")


def test_money_field_from_db_value_handles_none():
    field = MoneyField(
        "price", currency="BTC", default="5", max_digits=9, decimal_places=2
    )
    assert field.from_db_value(None, None, None, None) is None


def test_money_field_from_db_value_checks_currency():
    field = MoneyField(
        "price", currency="BTC", default="5", max_digits=9, decimal_places=2
    )
    invalid = Money(1, "USD")
    with pytest.raises(ValueError):
        field.from_db_value(invalid, None, None, None)


def test_money_field_from_db_value_checks_min_value():
    field = MoneyField(
        "price", currency="BTC", default="5", max_digits=9, decimal_places=2
    )
    invalid = Money(1, "USD")
    with pytest.raises(ValueError):
        field.from_db_value(invalid, None, None, None)


def test_money_field_formfield():
    field = MoneyField(
        "price", currency="BTC", default="5", max_digits=9, decimal_places=2
    )
    form_field = field.formfield()
    assert isinstance(form_field, forms.MoneyField)
    assert form_field.currency == "BTC"
    assert isinstance(form_field.widget, widgets.MoneyInput)


def test_price_field_init():
    field = TaxedMoneyField(net_field="price_net", gross_field="price_gross")
    assert field.net_field == "price_net"
    assert field.gross_field == "price_gross"


def test_compare_taxed_money_field_with_same_type_field():
    field_1 = TaxedMoneyField(net_field="price_net", gross_field="price_gross")
    field_2 = TaxedMoneyField(net_field="price_net", gross_field="price_gross")

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


def test_compare_taxed_money_field_with_django_field():
    field_1 = TaxedMoneyField(net_field="price_net", gross_field="price_gross")
    field_2 = MoneyField(currency="BTC", default="5", max_digits=9, decimal_places=2)

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


@pytest.mark.parametrize(
    "data,initial,expected_result",
    [
        ("5", Money(5, "BTC"), False),
        ("5", Money(10, "BTC"), True),
        ("5", "5", False),
        ("5", "10", True),
        ("5", None, True),
        (None, Money(5, "BTC"), True),
        (None, "5", True),
        (None, None, False),
    ],
)
def test_form_changed_data(data, initial, expected_result):
    form = RequiredPriceForm(data={"price_net": data}, initial={"price_net": initial})
    assert bool(form.changed_data) == expected_result


def test_render():
    widget = widgets.MoneyInput("BTC", attrs={"type": "number"})
    result = widget.render("price", 5, attrs={"foo": "bar"})
    attrs = ['foo="bar"', 'name="price"', 'type="number"', 'value="5"', "BTC"]
    for attr in attrs:
        assert attr in result


def test_instance_values():
    instance = Model(price_net=Money(25, "BTC"))
    assert instance.price.net.amount == 25


def test_instance_values_both_amounts():
    instance = Model(price_net=Money(25, "BTC"), price_gross=Money(30, "BTC"))
    assert instance.price == TaxedMoney(net=Money(25, "BTC"), gross=Money(30, "BTC"))


def test_instance_values_different_currencies():
    model = Model(price_net=Money(25, "BTC"), price_gross=Money(30, "USD"))
    with pytest.raises(ValueError):
        assert model.price


def test_instance_save_values_different_currency(db):
    model = Model()
    model.price_gross = Money(10, "USD")
    with pytest.raises(ValueError):
        model.save()


def test_instance_full_lean_values_different_currency(db):
    model = Model(price_gross=Money(10, "USD"))
    with pytest.raises(ValueError):
        model.full_clean()


def test_instance_full_clean_values_invalid_amount(db):
    model = Model(price_gross=Money("10.999", "BTC"))
    with pytest.raises(ValidationError):
        model.full_clean()


def test_set_instance_values():
    instance = Model()
    instance.price = TaxedMoney(Money(25, "BTC"), Money(30, "BTC"))
    assert instance.price_net == Money(25, "BTC")
    assert instance.price_gross == Money(30, "BTC")


def test_init_taxedmoney_model_field():
    instance = Model(price=TaxedMoney(Money(25, "BTC"), Money(30, "BTC")))
    assert instance.price_net == Money(25, "BTC")
    assert instance.price_gross == Money(30, "BTC")


def test_init_taxedmoney_model_field_validation():
    instance = Model(price=TaxedMoney(Money(25, "USD"), Money(30, "USD")))
    with pytest.raises(ValueError):
        instance.full_clean()


def test_combined_field_validation():
    instance = Model()
    instance.price = TaxedMoney(Money(25, "USD"), Money(30, "USD"))
    with pytest.raises(ValueError):
        instance.full_clean()


def test_field_passes_all_validations():
    form = RequiredPriceForm(data={"price_net": "20"})
    form.full_clean()
    assert form.errors == {}


def test_model_field_passes_all_validations():
    form = ModelForm(data={"price_net": "20", "price_gross": "25"})
    form.full_clean()
    assert form.errors == {}


def test_field_passes_none_validation():
    form = OptionalPriceForm(data={"price": None})
    form.full_clean()
    assert form.errors == {}


def test_validate_max_money():
    validator = MaxMoneyValidator(Money(5, "BTC"))
    validator(Money("5.00", "BTC"))
    with pytest.raises(ValidationError):
        validator(Money("5.01", "BTC"))
    with pytest.raises(ValueError):
        validator(Money("5.00", "USD"))


def test_validate_min_money():
    validator = MinMoneyValidator(Money(5, "BTC"))
    validator(Money("5.00", "BTC"))
    with pytest.raises(ValidationError):
        validator(Money("4.99", "BTC"))
    with pytest.raises(ValueError):
        validator(Money("5.00", "USD"))


def test_validate_money_precision():
    validator = MoneyPrecisionValidator("USD", 9, 2)
    validator(Money("5.00", "USD"))
    validator(Money("5.1", "USD"))
    with pytest.raises(ValidationError):
        validator(Money("5.001", "USD"))
    with pytest.raises(ValueError):
        validator(Money("5.00", "BTC"))


def test_validate_money_precision_by_currency():
    # Validator tests if precision is valid for given currency
    validator = MoneyPrecisionValidator("USD", 9, 3)
    validator(Money("5.00", "USD"))
    validator(Money("5.1", "USD"))
    with pytest.raises(ValidationError):
        validator(Money("5.001", "USD"))


def test_validate_money_precision_fictional_currency():
    validator = MoneyPrecisionValidator("BTC", 16, 10)
    validator(Money("5.1234567890", "BTC"))
    with pytest.raises(ValidationError):
        validator(Money("5.12345678901", "BTC"))


def test_validators_work_with_formfields():
    form = ValidatedPriceForm(data={"price": "25"})
    form.full_clean()
    assert form.errors == {
        "price": ["Ensure this value is less than or equal to $15.00."]
    }


def test_templatetag_discount_amount_for():
    price = TaxedMoney(Money(30, "BTC"), Money(30, "BTC"))

    discount = functools.partial(percentage_discount, percentage=50)
    discount_amount = prices.discount_amount_for(discount, price)
    assert discount_amount == TaxedMoney(Money(-15, "BTC"), Money(-15, "BTC"))


def test_non_existing_locale(money_fixture):
    # Test detecting an error that occur for language 'zh_CN' for which
    # the canonical code is 'zh_Hans_CN', see:
    #     Babel 1.0+ doesn't support `zh_CN`
    #     https://github.com/python-babel/babel/issues/37
    # Though to make this test more reliable we mock the language with totally
    # made up code 'oO_Oo' as the 'zh_CN' "alias" might work in the future, see:
    #     Babel needs to support Fuzzy Locales
    #     https://github.com/python-babel/babel/issues/30
    translation.activate("oO_Oo")
    amount = prices_i18n.amount(money_fixture, format="html")
    assert amount  # No exception, success!


def test_non_cannonical_locale_zh_CN(money_fixture, settings):
    # Test detecting an error that occur for language 'zh_CN' for which
    # the canonical code is 'zh_Hans_CN', see:
    #     Babel 1.0+ doesn't support `zh_CN`
    #     https://github.com/python-babel/babel/issues/37
    # This should now work, as we are using:
    #     `Locale.parse('zh_CN')`
    # which does the conversion to the canonical name.

    # Making sure the default "LANGUAGE_CODE" is "en_US"
    settings.LANGUAGE_CODE = "en_US"

    # Checking format of the default locale
    amount = prices_i18n.amount(money_fixture, format="html")
    assert amount == '<span class="currency">$</span>10.00'

    # Checking if 'zh_CN' has changed the format
    translation.activate("zh_CN")
    amount = prices_i18n.amount(money_fixture, format="html")
    assert amount == '<span class="currency">US$</span>10.00'  # 'US' before '$'


def test_templatetag_amount(money_fixture):
    amount = prices.amount(money_fixture)
    assert amount == '10 <span class="currency">USD</span>'


def test_templatetag_i18n_amount(money_fixture):
    amount = prices_i18n.amount(money_fixture)
    assert amount == "$10.00"


def test_templatetag_i18n_amount_html(money_fixture):
    amount = prices_i18n.amount(money_fixture, format="html")
    assert amount == '<span class="currency">$</span>10.00'


def test_templatetag_i18n_amount_wrong_param(money_fixture):
    amount = prices_i18n.amount(money_fixture, format="test")
    assert amount == "$10.00"


def test_get_currency_fraction_USD():
    result = prices_i18n.get_currency_fraction("USD")
    assert result == 2


def test_get_currency_fraction_unknown_currency():
    result = prices_i18n.get_currency_fraction(("test"))
    assert result == 2


def test_format_price_invalid_value():
    result = prices_i18n.format_price("invalid", "USD")
    assert result == ""


def test_money_currency_field_init():
    field = MoneyCurrencyField(
        amount_field="money_net_amount", currency_field="currency"
    )
    assert field.amount_field == "money_net_amount"
    assert field.currency_field == "currency"


def test_compare_money_currency_field_with_same_type_field():
    field_1 = MoneyCurrencyField(
        amount_field="money_net_amount", currency_field="currency"
    )
    field_2 = MoneyCurrencyField(
        amount_field="money_net_amount", currency_field="currency"
    )

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


def test_compare_money_currency_field_with_django_field():
    field_1 = MoneyCurrencyField(
        amount_field="money_net_amount", currency_field="currency"
    )
    field_2 = MoneyField(currency="BTC", default="5", max_digits=9, decimal_places=2)

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


def test_money_currency_instance_values():
    instance = CurrencyModel(money_net_amount=Decimal("10"), currency="USD")
    assert instance.money_net.amount == Decimal("10")
    assert instance.money_net.currency == "USD"
    assert instance.money_net == Money("10", "USD")


def test_money_currency_set_instance_values():
    instance = CurrencyModel()
    instance.money_net = Money(25, "USD")
    assert instance.money_net_amount == 25
    assert instance.currency == "USD"


def test_taxed_money_currency_instance_values():
    instance = CurrencyModel(
        money_net_amount=Decimal("10"), currency="USD", money_gross_amount=Decimal("11")
    )

    assert instance.money_gross.amount == Decimal("11")
    assert instance.money_gross.currency == "USD"
    assert instance.taxed_money.net.amount == Decimal("10")
    assert instance.taxed_money.net.currency == "USD"
    assert instance.taxed_money.gross.amount == Decimal("11")
    assert instance.taxed_money.gross.currency == "USD"


def test_taxed_money_currency_set_instance_values():
    instance = CurrencyModel()
    instance.taxed_money = TaxedMoney(Money(25, "USD"), Money(30, "USD"))
    assert instance.money_net_amount == 25
    assert instance.currency == "USD"
    assert instance.money_gross.amount == 30
    assert instance.money_gross.currency == "USD"


def test_taxed_money_currency_init_model_field():
    instance = CurrencyModel(money_net=Money(10, "USD"))
    assert instance.money_net_amount == 10
    assert instance.currency == "USD"
