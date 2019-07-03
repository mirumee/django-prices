from django import forms
from django.template.loader import render_to_string
from prices import Money

__all__ = ["MoneyInput", "FixedCurrencyMoneyInput"]


class MoneyInput(forms.MultiWidget):
    def __init__(self, choices, attrs=None):
        widgets = [
            forms.TextInput(attrs={"type": "number", "step": "any"}),
            forms.Select(choices=choices),
        ]
        super(MoneyInput, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value and isinstance(value, Money):
            return [value.amount, value.currency]
        return [None, None]


class FixedCurrencyMoneyInput(forms.MultiWidget):
    template = "prices/widget.html"

    def __init__(self, currency, attrs=None):
        self.currency = currency
        widgets = [
            forms.TextInput(attrs={"type": "number", "step": "any"}),
            forms.HiddenInput(),
        ]
        super(FixedCurrencyMoneyInput, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value and isinstance(value, Money):
            return [value.amount, self.currency]
        return [None, None]

    def render(self, name, value, attrs=None, renderer=None):
        widget = super(FixedCurrencyMoneyInput, self).render(
            name, value, attrs=attrs, renderer=renderer
        )
        return render_to_string(
            self.template, {"widget": widget, "value": value, "currency": self.currency}
        )
