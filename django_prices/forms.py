import itertools

from django import forms
from prices import Money

from .validators import (
    MaxMoneyValidator,
    MinMoneyValidator,
    MoneyPrecisionValidator,
    ValidationError,
)
from .widgets import FixedCurrencyMoneyInput, MoneyInput

__all__ = ("MoneyField", "MoneyInput")


class MoneyField(forms.MultiValueField):
    def __init__(
        self,
        available_currencies,
        widget=MoneyInput,
        max_values=None,
        min_values=None,
        max_digits=None,
        decimal_places=None,
        validators=(),
        *args,
        **kwargs
    ):
        decimal_field = forms.DecimalField(
            max_digits=max_digits, decimal_places=decimal_places
        )
        fields = (decimal_field, forms.ChoiceField(choices=available_currencies))
        if isinstance(widget, type):
            widget_instance = widget(available_currencies)
            if (
                isinstance(widget_instance, MoneyInput)
                and len(available_currencies) <= 1
            ):
                widget_instance = FixedCurrencyMoneyInput(
                    currency=available_currencies[0]
                    if len(available_currencies) == 1
                    else "",
                    attrs={"type": "number", "step": "any"},
                )
                fields = (decimal_field, forms.CharField())

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

    def compress(self, data_list):
        if data_list:
            # Raise a validation error if any of the values is empty
            # (it is possible if field has required=False)
            if data_list[0] in self.empty_values:
                raise ValidationError("Enter a valid amount of money")
            if data_list[1] in self.empty_values:
                raise ValidationError("Enter a valid currency code")
            return Money(data_list[0], data_list[1])
        return None
