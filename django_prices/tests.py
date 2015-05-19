from decimal import Decimal
from unittest import TestCase

import django
from django.db import models
from prices import Price

from . import forms
from .models import PriceField
from . import widgets


class Foo(models.Model):

    price = PriceField('price', currency='BTC', default='5', max_digits=9,
                       decimal_places=2)


class PriceFieldTest(TestCase):

    def test_init(self):
        foo = Foo()
        self.assertEquals(foo.price, Price(5, currency='BTC'))

    def test_get_prep_value(self):
        field = PriceField('price', currency='BTC', default='5', max_digits=9,
                           decimal_places=2)
        self.assertEquals(field.get_prep_value(Price(5, currency='BTC')),
                          Decimal(5))

    def test_to_python(self):
        field = PriceField('price', currency='BTC', default='5', max_digits=9,
                           decimal_places=2)
        self.assertEqual(field.to_python(7), Price(7, currency='BTC'))

    def test_to_python_handles_none(self):
        field = PriceField('price', currency='BTC', default='5', max_digits=9,
                           decimal_places=2)
        self.assertEqual(field.to_python(None), None)

    def test_to_python_checks_currency(self):
        field = PriceField('price', currency='BTC', default='5', max_digits=9,
                           decimal_places=2)
        invalid = Price(1, currency='USD')
        self.assertRaises(ValueError, lambda: field.to_python(invalid))

    def test_formfield(self):
        field = PriceField('price', currency='BTC', default='5', max_digits=9,
                           decimal_places=2)
        form_field = field.formfield()
        self.assertTrue(isinstance(form_field, forms.PriceField))
        self.assertEqual(form_field.currency, 'BTC')
        self.assertTrue(isinstance(form_field.widget, widgets.PriceInput))


class PriceInputTest(TestCase):

    def setUp(self):
        django.setup()

    def test_render(self):
        widget = widgets.PriceInput('BTC', attrs={'type': 'number'})
        result = widget.render('price', 5, attrs={'foo': 'bar'})
        self.assertEqual(
            result,
            '<input foo="bar" name="price" type="number" value="5" /> BTC')
