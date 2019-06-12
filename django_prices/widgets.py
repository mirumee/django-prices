from django import forms
from prices import Money

__all__ = ["MoneyInput"]


class MoneyInput(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            forms.TextInput(attrs={"type": "number", "step": "any"}),
            forms.TextInput(),
        ]
        super(MoneyInput, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value and isinstance(value, Money):
            return [value.amount, value.currency]
        if value and isinstance(value, (list, tuple)) and len(value) == 2:
            return value
        return [None, None]
