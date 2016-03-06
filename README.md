django-prices: Django fields for the `prices` module
====================================================

[![Build Status](https://secure.travis-ci.org/mirumee/django-prices.png)](https://travis-ci.org/mirumee/django-prices) [![codecov.io](https://img.shields.io/codecov/c/github/mirumee/django-prices/master.svg)](http://codecov.io/github/mirumee/django-prices?branch=master)

Provides support for models:

```python
from django.db import models

from django_prices.models import PriceField

class Product(models.Model):
    name = models.CharField('Name')
    price = PriceField('Price', currency='BTC', max_digits=12, decimal_places=2)
```

And forms:

```python
from django import forms

from django_prices.forms import PriceField

class ProductForm(forms.Form):
    name = forms.CharField(label='Name')
    price = PriceField(label='Price', currency='BTC')
```

And templates:

```html+django
{% load prices %}

<p>Price: {% gross foo.price %} ({% net foo.price %} + {% tax foo.price %} tax)</p>
```

**Note:** for template tags to work, you need to add `django_prices` to your `INSTALLED_APPS`.

You can also install the wonderful [`babel`](http://babel.pocoo.org/) library and get proper currency symbols with `prices_i18n`. First install BabelDjango:

```
$ pip install BabelDjango
```

Then follow the instruction to add it to your `INSTALLED_APPS` and `MIDDLEWARE_CLASSES`. Finally load the localized template tags:

```html+django
{% load prices_i18n %}

<p>Price: {% gross foo.price %} ({% net foo.price %} + {% tax foo.price %} tax)</p>
```

You can also use HTML output from `prices_i18n` template tags, they will wrap currency symbol in a `<span>` element:

```html+django
{% load prices_i18n %}

<p>Price: {% gross foo.price html=True %} ({% net foo.price html=True %} + {% tax foo.price html=True %} tax)</p>
```

It will be rendered as a following structure (for example with English locale):

```html
<span class="currency">$</span>15.00
```


Batteries included: django-prices comes with South migration support.
