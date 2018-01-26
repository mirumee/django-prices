django-prices: Django fields for the `prices` module
====================================================

[![Build Status](https://secure.travis-ci.org/mirumee/django-prices.png)](https://travis-ci.org/mirumee/django-prices) [![codecov.io](https://img.shields.io/codecov/c/github/mirumee/django-prices/master.svg)](http://codecov.io/github/mirumee/django-prices?branch=master)

Provides support for models:

```python
from django.db import models

from django_prices.models import MoneyField, TaxedMoneyField

class Product(models.Model):
    name = models.CharField('Name')
    price_net = MoneyField(
        'net', currency='BTC', default='5', max_digits=9,
        decimal_places=2)
    price_gross = MoneyField(
        'gross', currency='BTC', default='5', max_digits=9,
        decimal_places=2)
    price = TaxedMoneyField(net_field='price_net', gross_field='price_gross')
```

And forms:

```python
from django import forms

from django_prices.forms import MoneyField

class ProductForm(forms.Form):
    name = forms.CharField(label='Name')
    price_net = MoneyField(label='net', currency='BTC')
```

And validators:

```python
from django import forms
from prices.forms import Money

from django_prices.forms import MoneyField
from django_prices.Validators import (
    MaxMoneyValidator, MinMoneyValidator, MoneyPrecisionValidator)

class DonateForm(forms.Form):
    donator_name = forms.CharField(label='Your name')
    donation = MoneyField(
        label='net', currency='EUR', max_digits=9, decimal_places=2,
        validators=[MoneyPrecisionValidator('EUR'),
                    MinMoneyValidator(Money(5, 'EUR')),
                    MaxMoneyValidator(Money(500, 'EUR'))])
```

And templates:

```html+django
{% load prices %}

<p>Price: {{ foo.price.gross|amount }} ({{ foo.price.net|amount }} + {{ foo.price.tax|amount }} tax)</p>
```

**Note:** for template tags to work, you need to add `django_prices` to your `INSTALLED_APPS`.

You can also install the wonderful [`babel`](http://babel.pocoo.org/) library and get proper currency symbols with `prices_i18n`. First install BabelDjango:

```
$ pip install BabelDjango
```

Then follow the instruction to add it to your `INSTALLED_APPS` and `MIDDLEWARE_CLASSES`. Finally load the localized template tags:

```html+django
{% load prices_i18n %}

<p>Price: {{ foo.price.gross|amount }} ({{ foo.price.net|amount }} + {{ foo.price.tax|amount }} tax)</p>
```

You can also use HTML output from `prices_i18n` template tags, they will wrap currency symbol in a `<span>` element:

```html+django
{% load prices_i18n %}

<p>Price: {{ foo.price.gross|amount:'html' }} ({{ foo.price.net|amount:'html' }} + {{ foo.price.tax|amount:'html' }} tax)</p>
```

It will be rendered as a following structure (for example with English locale):

```html
<span class="currency">$</span>15.00
```
