# coding: utf-8
from __future__ import unicode_literals

import functools
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db.models import DecimalField
from django.utils import translation
from django_prices import forms, widgets
from django_prices.models import MoneyField, TaxedMoneyField
from django_prices.templatetags import prices, prices_i18n
from django_prices.validators import (
    MaxMoneyValidator,
    MinMoneyValidator,
    MoneyPrecisionValidator,
)
from prices import Money, TaxedMoney, percentage_discount

from .forms import (
    AVAILABLE_CURRENCIES,
    MaxMinPriceForm,
    ModelForm,
    OptionalPriceForm,
    RequiredPriceForm,
    ValidatedPriceForm,
)
from .models import Model, NullModel


@pytest.fixture(scope="module")
def money_fixture():
    return Money("10", "USD")


def test_money_field_init():
    field = MoneyField(amount_field="amount", currency_field="currency")
    assert field.get_default() == Money(0, None)
    assert field.amount_field == "amount"
    assert field.currency_field == "currency"


def test_money_field_formfield_returns_form_with_fixed_currency_input_if_no_model_attached():
    field = MoneyField(amount_field="amount", currency_field="currency")
    form_field = field.formfield()
    assert isinstance(form_field, forms.MoneyField)
    assert isinstance(form_field.widget, widgets.FixedCurrencyMoneyInput)


def test_money_field_formfield_returns_form_with_select_input_if_choices_are_defined_for_currency_field():
    field = Model.price_net
    form_field = field.formfield()
    assert isinstance(form_field, forms.MoneyField)
    assert isinstance(form_field.widget, widgets.MoneyInput)


def test_compare_money_field_with_same_type_field():
    field_1 = MoneyField(amount_field="money_net_amount", currency_field="currency")
    field_2 = MoneyField(amount_field="money_net_amount", currency_field="currency")

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


def test_compare_money_field_with_django_field():
    field_1 = MoneyField(amount_field="money_net_amount", currency_field="currency")
    field_2 = DecimalField(default="5", max_digits=9, decimal_places=2)

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


def test_compare_money_field_with_taxed_money_field():
    field_1 = MoneyField(amount_field="money_net_amount", currency_field="currency")
    field_2 = TaxedMoneyField(net_field="price_net", gross_field="price_gross")

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


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


def test_taxed_money_field_init():
    field = TaxedMoneyField(
        net_amount_field="price_net",
        gross_amount_field="price_gross",
        currency="currency",
    )
    assert field.net_amount_field == "price_net"
    assert field.gross_amount_field == "price_gross"
    assert field.currency == "currency"


def test_compare_taxed_money_field_with_same_type_field():
    field_1 = TaxedMoneyField(
        net_amount_field="price_net",
        gross_amount_field="price_gross",
        currency="currency",
    )
    field_2 = TaxedMoneyField(
        net_amount_field="price_net",
        gross_amount_field="price_gross",
        currency="currency",
    )

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


def test_compare_taxed_money_field_with_django_field():
    field_1 = TaxedMoneyField(
        net_amount_field="price_net",
        gross_amount_field="price_gross",
        currency="currency",
    )
    field_2 = DecimalField(default="5", max_digits=9, decimal_places=2)

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


def test_compare_taxed_money_field_with_money_field():
    field_1 = TaxedMoneyField(
        net_amount_field="price_net",
        gross_amount_field="price_gross",
        currency="currency",
    )
    field_2 = MoneyField(amount_field="money_net_amount", currency_field="currency")

    # Comparision is based on creation_counter attribute
    assert field_1 < field_2
    field_2.creation_counter -= 1
    assert field_1 == field_2


@pytest.mark.parametrize(
    "data,initial,expected_result",
    [
        (["5", "BTC"], Money(5, "BTC"), False),
        (["5", "BTC"], Money(10, "BTC"), True),
        (["5", "BTC"], ["5", "BTC"], False),
        (["5", "BTC"], ["5", "USD"], True),
        (["5", "BTC"], None, True),
        ([None, None], Money(5, "BTC"), True),
        ([None, None], ["5", "BTC"], True),
        ([None, None], None, False),
    ],
)
def test_form_changed_data(data, initial, expected_result):
    form = RequiredPriceForm(
        data={"price_net_0": data[0], "price_net_1": data[1]},
        initial={"price_net": initial},
    )
    assert bool(form.changed_data) == expected_result


def test_form_changed_when_only_one_value_is_changed():
    form = RequiredPriceForm(
        data={"price_net_0": "5"}, initial={"price_net": Money(10, "BTC")}
    )
    assert bool(form.changed_data) == True
    form = RequiredPriceForm(
        data={"price_net_1": "USD"}, initial={"price_net": Money(10, "BTC")}
    )
    assert bool(form.changed_data) == True


def test_render_money_input():
    widget = widgets.MoneyInput(choices=[("USD", "US dollar")], attrs={"key": "value"})
    result = widget.render("price", Money(5, "USD"), attrs={"foo": "bar"})
    assert 'foo="bar"' in result
    assert 'name="price_0"' in result
    assert 'name="price_1"' in result
    assert 'key="value"' in result
    assert 'value="5"' in result
    assert "USD" in result


def test_render_fixed_currency_money_input():
    widget = widgets.FixedCurrencyMoneyInput(currency="BTC", attrs={"key": "value"})
    result = widget.render("price", Money(5, "BTC"), attrs={"foo": "bar"})
    attrs = ['foo="bar"', 'key="value"', 'value="5"', "price_0", "BTC"]
    for attr in attrs:
        assert attr in result


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


def test_form_field_passes_all_validations_for_correct_money_value():
    form = RequiredPriceForm(data={"price_net_0": "20", "price_net_1": "BTC"})
    form.full_clean()
    assert form.errors == {}


def test_form_field_passes_all_validations_for_correct_taxed_money_value():
    form = ModelForm(
        data={
            "price_net_0": "20",
            "price_net_1": "BTC",
            "price_gross_0": "25",
            "price_gross_1": "BTC",
        }
    )
    form.full_clean()
    assert form.errors == {}


def test_form_field_validation_passes_if_both_values_are_none():
    form = OptionalPriceForm(data={"price_net_0": None, "price_net_1": None})
    form.full_clean()
    assert form.errors == {}


def test_form_field_validation_fails_if_only_currency_is_given():
    form = OptionalPriceForm(data={"price_net_0": None, "price_net_1": "USD"})
    form.full_clean()
    assert form.errors == {"price_net": ["Enter a valid amount of money"]}


def test_form_field_validation_fails_if_too_many_max_digits():
    form = ValidatedPriceForm(data={"price_0": 15000000000, "price_1": "USD"})
    form.full_clean()
    assert form.errors == {
        "price": ["Ensure that there are no more than 9 digits in total."]
    }


def test_form_field_validation_fails_if_too_many_decimal_places():
    form = ValidatedPriceForm(data={"price_0": "5.005", "price_1": "USD"})
    form.full_clean()
    assert form.errors == {
        "price": ["Ensure that there are no more than 2 decimal places."]
    }


def test_form_field_validation_fails_if_nonavailable_currency():
    assert "EUR" not in AVAILABLE_CURRENCIES
    form = RequiredPriceForm(data={"price_net_0": "20", "price_net_1": "EUR"})
    assert form.errors == {
        "price_net": ["Select a valid choice. EUR is not one of the available choices."]
    }


def test_max_money_validation_raises_error_if_greater_money():
    validator = MaxMoneyValidator(Money(5, "BTC"))
    validator(Money("5.00", "BTC"))
    with pytest.raises(ValidationError):
        validator(Money("5.01", "BTC"))


def test_min_money_validation_raises_error_if_less_money():
    validator = MinMoneyValidator(Money(5, "BTC"))
    validator(Money("5.00", "BTC"))
    with pytest.raises(ValidationError):
        validator(Money("4.99", "BTC"))


def test_max_money_validation_passes_if_greater_amount_is_in_different_currency():
    """It's incomparable, so it should be accepted."""
    validator = MaxMoneyValidator(Money(5, "BTC"))
    validator(Money("5.00", "USD"))
    validator(Money("5.01", "USD"))


def test_min_money_validation_passes_if_less_amount_is_in_different_currency():
    """It's incomparable, so it should be accepted."""
    validator = MinMoneyValidator(Money(5, "BTC"))
    validator(Money("5.00", "USD"))
    validator(Money("4.99", "USD"))


def test_validate_money_precision():
    validator = MoneyPrecisionValidator(9, 2)
    validator(Money("5.00", "USD"))
    validator(Money("5.1", "USD"))
    with pytest.raises(ValidationError):
        validator(Money("5.001", "USD"))


def test_validate_money_precision_by_currency():
    # Validator tests if precision is valid for given currency
    validator = MoneyPrecisionValidator(9, 3)
    validator(Money("5.00", "USD"))
    validator(Money("5.1", "USD"))
    with pytest.raises(ValidationError):
        validator(Money("5.001", "USD"))


def test_validate_money_precision_fictional_currency():
    validator = MoneyPrecisionValidator(16, 10)
    validator(Money("5.1234567890", "BTC"))
    with pytest.raises(ValidationError):
        validator(Money("5.12345678901", "BTC"))


def test_validators_work_with_formfields():
    form = ValidatedPriceForm(data={"price_0": "25", "price_1": "USD"})
    form.full_clean()
    assert form.errors == {
        "price": ["Ensure this value is less than or equal to $15.00."]
    }


def test_define_max_money_validators_for_many_currencies():
    form = MaxMinPriceForm(data={"price_0": "1", "price_1": "USD"})
    form.full_clean()
    assert form.errors == {
        "price": ["Ensure this value is greater than or equal to $5.00."]
    }
    form = MaxMinPriceForm(data={"price_0": "1", "price_1": "BTC"})
    form.full_clean()
    assert form.errors == {
        "price": ["Ensure this value is greater than or equal to BTC6.00."]
    }


def test_define_min_money_validators_for_many_currencies():
    form = MaxMinPriceForm(data={"price_0": "15.01", "price_1": "USD"})
    form.full_clean()
    assert form.errors == {
        "price": ["Ensure this value is less than or equal to $15.00."]
    }
    form = MaxMinPriceForm(data={"price_0": "16.01", "price_1": "BTC"})
    form.full_clean()
    assert form.errors == {
        "price": ["Ensure this value is less than or equal to BTC16.00."]
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


def test_get_default_values():
    object_with_defaults = Model()
    net = Money(Model.DEFAULT_NET, currency=Model.DEFAULT_CURRENCY)
    gross = Money(Model.DEFAULT_GROSS, currency=Model.DEFAULT_CURRENCY)
    assert object_with_defaults.price_net == net
    assert object_with_defaults.price_net == gross
    assert object_with_defaults.price == TaxedMoney(net, gross)


def test_get_default_values_wth_nulls():
    object_with_defaults = NullModel()
    net = None
    gross = None
    assert object_with_defaults.price_net is None
    assert object_with_defaults.price_net is None
    assert object_with_defaults.price is None
