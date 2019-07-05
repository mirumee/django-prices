# coding: utf-8
import pytest
from django.core.exceptions import ValidationError
from django_prices.validators import (
    MaxMoneyValidator,
    MinMoneyValidator,
    MoneyPrecisionValidator,
)
from prices import Money


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
