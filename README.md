django-prices: Django fields for the `prices` module
====================================================

Provides support for models:

```python
from django.db import models

from django_prices.models import PriceField

class Product(models.Model):
    name = models.CharField('Name')
    price = PriceField('Price', currency='BTC')
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

```
{% load prices %}

<p>Price: {% gross foo.price %} ({% net foo.price %} + {% tax foo.price %} tax)</p>
```

Or install the wonderful [`babel`](http://babel.edgewall.org/) library and get proper currency symbols with `prices_i18n`:

```
$ pip install babel
```

```
{% load prices_i18n %}

<p>Price: {% gross foo.price %} ({% net foo.price %} + {% tax foo.price %} tax)</p>
```

Batteries included: django-prices comes with South migration support.
