from django import forms
from prices import Price

__all__ = ('PriceInput',)


class PriceInput(forms.TextInput):

    def __init__(self, currency, *args, **kwargs):
        self.currency = currency
        super(PriceInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        amount = ''
        if isinstance(value, Price):
            value = value.net
        result = super(PriceInput, self).render(name, amount)
        result += u' %s' % (self.currency,)
        return result
