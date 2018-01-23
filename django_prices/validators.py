from babel.numbers import get_currency_precision
from django.core.validators import (
    DecimalValidator, MaxValueValidator, MinValueValidator, ValidationError)

from .templatetags.prices_i18n import format_price


class MoneyPrecisionValidator(DecimalValidator):
    def __init__(self, currency, max_digits=None, **options):
        self.currency = currency
        super(MoneyPrecisionValidator, self).__init__(
            max_digits=max_digits,
            decimal_places=get_currency_precision(currency),
            **options)

    def __call__(self, other):
        if self.currency != other.currency:
            raise ValueError(
                'Cannot validate amounts that are not in %r (value was %r)' % (
                    self.currency, other.currency ))
        super(MoneyPrecisionValidator, self).__call__(other.amount)


class MoneyValueValidator:
    def __call__(self, value):
        cleaned = self.clean(value)
        if self.compare(cleaned, self.limit_value):
            currency = self.limit_value.currency
            params = {
                'limit_value': format_price(self.limit_value.amount, currency),
                'show_value': format_price(cleaned.amount, currency),
                'value': format_price(value.amount, currency)}
            raise ValidationError(
                self.message, code=self.code, params=params)


class MaxMoneyValidator(MoneyValueValidator, MaxValueValidator):
    pass


class MinMoneyValidator(MoneyValueValidator, MinValueValidator):
    pass
