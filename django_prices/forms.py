import itertools
from decimal import Decimal
from typing import List, Optional, Tuple

from babel.numbers import get_currency_symbol
from django import forms
from django.core.validators import ValidationError
from prices import Money

from .utils.locale import get_locale_data
from .validators import MaxMoneyValidator, MinMoneyValidator, MoneyPrecisionValidator
from .widgets import FixedCurrencyMoneyInput, MoneyInput

__all__ = ("MoneyField", "MoneyInput")


def _get_symbol(currency_code: str) -> str:
    _, locale_code = get_locale_data()
    return get_currency_symbol(currency_code, locale_code)


def _get_currency_choices(currencies: List[str]) -> List[Tuple[str, str]]:
    """Generate choices for SelectField.
    As a label we are presenting currency symbol."""
    currency_choices = [(code, _get_symbol(code)) for code in currencies]
    return currency_choices


class MoneyField(forms.MultiValueField):
    """A field for Money objects.

    When only one currency is provided, it renders as FixedCurrencyMoneyInput,
    when more you will get MoneyInput which allow you to choose both amount
    and currency.

    `available_currencies` argument is expected to be list of currency codes."""

    def __init__(
        self,
        available_currencies: List[str],
        widget=None,
        max_values: Optional[List] = None,
        min_values: Optional[List] = None,
        max_digits: int = None,
        decimal_places: int = None,
        validators=(),
        *args,
        **kwargs
    ):
        decimal_field = forms.DecimalField(
            max_digits=max_digits, decimal_places=decimal_places
        )

        choices = _get_currency_choices(available_currencies)
        fields = (decimal_field, forms.ChoiceField(choices=choices))

        if widget is not None:
            raise NotImplementedError("Custom widgets are not supported by MoneyField.")

        if len(available_currencies) == 0:
            raise ValueError("At least one currency needed.")
        elif len(available_currencies) == 1:
            widget_instance = FixedCurrencyMoneyInput(
                currency=_get_symbol(available_currencies[0])
            )
        else:
            widget_instance = MoneyInput(
                choices=_get_currency_choices(available_currencies)
            )

        super(MoneyField, self).__init__(
            fields, widget=widget_instance, *args, **kwargs
        )

        self.validators = list(itertools.chain(self.default_validators, validators))
        self.validators.append(MoneyPrecisionValidator(max_digits, decimal_places))
        if max_values is not None:
            self.validators.extend(
                [MaxMoneyValidator(limit_value) for limit_value in max_values]
            )
        if min_values is not None:
            self.validators.extend(
                [MinMoneyValidator(limit_value) for limit_value in min_values]
            )

    def compress(self, data_list: Optional[Tuple[Decimal, str]]) -> Optional[Money]:
        """If field is optional, return None when there is no amount provided."""
        if not data_list:
            return None

        amount, currency = data_list
        if amount in self.empty_values and self.required:
            raise ValidationError("Enter a valid amount of money")
        if currency in self.empty_values and self.required:
            raise ValidationError("Enter a valid currency code")

        if amount is None:
            return None

        return Money(amount, currency)
