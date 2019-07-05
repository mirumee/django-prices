# coding: utf-8
import pytest
from django_prices import forms, widgets
from prices import Money

from .forms import (
    AVAILABLE_CURRENCIES,
    MaxMinPriceForm,
    ModelForm,
    OptionalPriceForm,
    RequiredPriceForm,
    ValidatedPriceForm,
    FixedCurrencyRequiredPriceForm,
    FixedCurrencyOptionalPriceForm,
)


def test_money_input_widget_renders():
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


def test_form_field_passes_all_validations_for_correct_money_value():
    form = RequiredPriceForm(data={"price_net_0": "20", "price_net_1": "BTC"})
    form.full_clean()
    assert form.errors == {}


def test_form_field_fixed_currency_andrequired_pass_on_valid_data():
    form = FixedCurrencyRequiredPriceForm(data={"price_0": "20", "price_1": "BTC"})
    form.full_clean()
    assert form.errors == {}
    assert form.cleaned_data["price"] == Money(20, "BTC")


def test_form_field_fixed_currency_and_required_error_on_wrong_currency():
    form = FixedCurrencyRequiredPriceForm(data={"price_0": "20", "price_1": "LOL"})
    form.full_clean()
    assert form.errors == {
        "price": ["Select a valid choice. LOL is not one of the available choices."]
    }


def test_form_field_fixed_currency_and_required_error_on_missing_amount():
    form = FixedCurrencyRequiredPriceForm(data={"price_1": "BTC"})
    form.full_clean()
    assert form.errors == {"price": ["This field is required."]}


def test_form_field_fixed_currency_and_optional_pass_on_valid_data():
    form = FixedCurrencyOptionalPriceForm(data={"price_0": "20", "price_1": "BTC"})
    form.full_clean()
    assert form.errors == {}
    assert form.cleaned_data["price"] == Money(20, "BTC")


def test_form_field_fixed_currency_and_optional_error_on_wrong_currency():
    form = FixedCurrencyOptionalPriceForm(data={"price_0": "20", "price_1": "LOL"})
    form.full_clean()
    assert form.errors == {
        "price": ["Select a valid choice. LOL is not one of the available choices."]
    }


def test_form_field_fixed_currency_and_optional_none_on_no_amount():
    form = FixedCurrencyOptionalPriceForm(data={"price_0": "", "price_1": "BTC"})
    form.full_clean()
    assert form.errors == {}
    assert form.cleaned_data["price"] is None


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
    form = RequiredPriceForm(data={"price_net_0": None, "price_net_1": "USD"})
    form.full_clean()
    assert form.errors == {"price_net": ["This field is required."]}


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


def test_validators_work_with_formfields():
    form = ValidatedPriceForm(data={"price_0": "25", "price_1": "USD"})
    form.full_clean()
    assert form.errors == {
        "price": ["Ensure this value is less than or equal to $15.00."]
    }


def test_max_money_is_validated_for_many_currencies():
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


def test_min_money_is_validated_for_many_currencies():
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


def test_value_error_is_raised_when_no_currencies_are_configured():
    with pytest.raises(ValueError):
        forms.MoneyField(available_currencies=[])
