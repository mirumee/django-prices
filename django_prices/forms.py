import itertools

from django import forms
from prices import Money

from .validators import (
    MaxMoneyValidator,
    MinMoneyValidator,
    MoneyPrecisionValidator,
    ValidationError,
)
from .widgets import MoneyConstCurrencyInput, MoneyInput

__all__ = ("MoneyField", "MoneyInput")


class MoneyField(forms.MultiValueField):
    def __init__(
        self,
        default_currency,
        available_currencies=None,
        widget=MoneyInput,
        max_value=None,
        min_value=None,
        max_digits=None,
        decimal_places=None,
        validators=(),
        *args,
        **kwargs
    ):
        self.default_currency = default_currency

        if isinstance(widget, type):
            widget_instance = widget(available_currencies)
            if isinstance(widget_instance, MoneyInput) and (
                available_currencies is None or len(available_currencies) <= 1
            ):
                widget_instance = MoneyConstCurrencyInput(
                    currency=default_currency, attrs={"type": "number", "step": "any"}
                )

        if available_currencies:
            fields = (
                forms.DecimalField(),
                forms.ChoiceField(choices=available_currencies),
            )
        else:
            fields = (forms.DecimalField(), forms.CharField())

        super(MoneyField, self).__init__(
            fields, widget=widget_instance, *args, **kwargs
        )

        self.validators = list(itertools.chain(self.default_validators, validators))
        self.validators.append(MoneyPrecisionValidator(max_digits, decimal_places))
        if max_value is not None:
            self.validators.append(MaxMoneyValidator(max_value))
        if min_value is not None:
            self.validators.append(MinMoneyValidator(min_value))

    def compress(self, data_list):
        if data_list:
            # Raise a validation error if one of the values are empty
            # (it is possible if field has required=False)
            if data_list[0] in self.empty_values:
                raise ValidationError("Enter a valid amount of money")
            if data_list[1] in self.empty_values:
                raise ValidationError("Enter a valid currency code")
            return Money(data_list[0], data_list[1])
        return None
