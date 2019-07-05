django-prices: Django fields for the `prices` module
====================================================

[![Build Status](https://secure.travis-ci.org/mirumee/django-prices.png)](https://travis-ci.org/mirumee/django-prices) [![codecov.io](https://img.shields.io/codecov/c/github/mirumee/django-prices/master.svg)](http://codecov.io/github/mirumee/django-prices?branch=master)

# Installation

* `pip install django-prices`
* Add `django_prices` to your `INSTALLED_APPS` at `settings.py`
* Follow `django-babel` [instructions](https://github.com/python-babel/django-babel/#using-the-middleware) and update both your `INSTALLED_APPS` and `MIDDLEWARE_CLASSES`.

# Features

Provides support for models:

```python
from django.db import models
from django_prices.models import MoneyField, TaxedMoneyField


class Model(models.Model):
    currency = models.CharField(max_length=3, default="BTC")
    price_net_amount = models.DecimalField(max_digits=9, decimal_places=2, default="5")
    price_net = MoneyField(amount_field="price_net_amount", currency_field="currency")
    price_gross_amount = models.DecimalField(
        max_digits=9, decimal_places=2, default="5"
    )
    price_gross = MoneyField(
        amount_field="price_gross_amount", currency_field="currency"
    )
    price = TaxedMoneyField(
        net_amount_field="price_net_amount",
        gross_amount_field="price_gross_amount",
        currency="currency",
    )
```

And forms:

```python
from django import forms

from django_prices.forms import MoneyField

AVAILABLE_CURRENCIES = [("BTC", "bitcoins"), ("USD", "US dollar")]


class ProductForm(forms.Form):
    name = forms.CharField(label="Name")
    price_net = MoneyField(label="net", available_currencies=AVAILABLE_CURRENCIES)
```

And validators:

```python
from django import forms
from prices.forms import Money

from django_prices.forms import MoneyField
from django_prices.validators import (
    MaxMoneyValidator, MinMoneyValidator, MoneyPrecisionValidator)


class DonateForm(forms.Form):
    donator_name = forms.CharField(label="Your name")
    donation = MoneyField(
        label="net",
        available_currencies=[("BTC", "bitcoins"), ("USD", "US dollar")],
        max_digits=9,
        decimal_places=2,
        validators=[
            MoneyPrecisionValidator(),
            MinMoneyValidator(Money(5, "USD")),
            MaxMoneyValidator(Money(500, "USD")),
        ],
    )
```

It also provides support for templates:

```html+django
{% load prices %}

<p>Price: {{ foo.price.gross|amount }} ({{ foo.price.net|amount }} + {{ foo.price.tax|amount }} tax)</p>
```


You can also use HTML output from `prices` template tags, they will wrap currency symbol in a `<span>` element:

```html+django
{% load prices %}

<p>Price: {{ foo.price.gross|amount:'html' }} ({{ foo.price.net|amount:'html' }} + {{ foo.price.tax|amount:'html' }} tax)</p>
```

It will be rendered as a following structure (for example with English locale):

```html
<span class="currency">$</span>15.00
```

## How to migrate to django-prices 2.0

Version 2.0 introduces major changes to how prices data is stored in models, enabling setting price's currency per model instance.

Steps to migrate:

1. In your **forms**:
    * remove the `currency` argument
    * add `available_currencies` with available choices.

    If the form specified `MoneyFields` in `fields` option, replace those with explicit declarations instead:

            ```python
            AVAILABLE_CURRENCIES = [("BTC", "bitcoins"), ("USD", "US dollar")]

            class ModelForm(forms.ModelForm):
                class Meta:
                    model = models.Model
                    fields = []

                price_net = MoneyField(available_currencies=AVAILABLE_CURRENCIES)
            ```

1. In your **models** using `MoneyField`:
    * Replace all occurrences of the `MoneyField` class with `DecimalField`
    * Remove the `currency` argument from them
    * Change `default` from Money instance to value acceptable by Decimal field

        Example of code:
        ```python
            price_net = MoneyField(
                "net", currency="BTC", default=Money("0", "BTC"), max_digits=9, decimal_places=2
            )
        ```
        Updated code:
        ```python
            price_net = models.DecimalField("net", default="5", max_digits=9, decimal_places=2)
        ```

1. In your **migration** files:
    * Replace all occurrences of the `MoneyField` class with `DecimalField`
    * Remove the `currency` argument from them
    * Change `default` from Money instance to value acceptable by Decimal field

        ```python
            field=django_prices.models.MoneyField(currency='BTC', decimal_places=2, default='5', max_digits=9, verbose_name='net')
        ```
        Updated code:
        ```python
            field=models.DecimalField(decimal_places=2, default='5', max_digits=9, verbose_name='net')
        ```

1. Rename fields in **models**. Your old field will still store amount of money, so probably the best choice would be `price_net_amount` instead `price_net`.

1. All places which use Models and it's fields can prevent django app from even starting the code. Possible issues: code tries to access non existing fields. Exclude those fields for now from your ModelForms, Graphene types etc.

1. Run `python manage.py makemigrations`. Make sure to do this step before adding new `MoneyFields` to model! If not, django will generate `delete/create` migrations instead of `rename`.

1. Run `python manage.py migrate`.

1. Update `django-prices`.

1. Add `models.CharField` for currency and `MoneyField` to your models:

    ```python
        currency = models.CharField(max_length=3, default="BTC")
        price_net_amount = models.DecimalField("net", default="5", max_digits=9, decimal_places=2)
        price_net = MoneyField(amount_field="price_net_amount", currency_field="currency")
    ```

1. Run `python manage.py makemigrations` and `python manage.py migrate`.

1. Change `TaxedMoneyField` declaration:

    ```python
        price = TaxedMoneyField(
            net_amount_field="price_net_amount",
            gross_amount_field="price_gross_amount",
            currency="currency",
        )
    ```

1. Remember to address changes in previously edited ModelForms
