import itertools

from django import forms
from prices import Money

from .validators import MaxMoneyValidator, MinMoneyValidator, MoneyPrecisionValidator
from .widgets import MoneyInput

__all__ = ("MoneyField", "MoneyInput")


class MoneyField(forms.MultiValueField):
    def __init__(
        self,
        default_currency,
        widget=MoneyInput,
        max_value=None,
        min_value=None,
        max_digits=None,
        decimal_places=None,
        validators=(),
        *args,
        **kwargs
    ):
        self.default_currency = default_currency or ""
        fields = (forms.DecimalField(), forms.CharField())
        super(MoneyField, self).__init__(fields, widget=widget, *args, **kwargs)

        self.validators = list(itertools.chain(self.default_validators, validators))
        self.validators.append(MoneyPrecisionValidator(max_digits, decimal_places))
        if max_value is not None:
            self.validators.append(MaxMoneyValidator(max_value))
        if min_value is not None:
            self.validators.append(MinMoneyValidator(min_value))

    def compress(self, data_list):
        if len(data_list) != 2:
            return Money(0, self.default_currency)
        return Money(data_list[0], data_list[1])
