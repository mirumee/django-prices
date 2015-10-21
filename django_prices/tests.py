from decimal import Decimal
from unittest import TestCase

import django
from prices import Price

from . import forms
from . import widgets
from .models import PriceField


class PriceFieldTest(TestCase):

    def test_init(self):
        field = PriceField(
            currency='BTC', default='5', max_digits=9, decimal_places=2)
        self.assertEquals(field.get_default(), Price(5, currency='BTC'))

    def test_get_prep_value(self):
        field = PriceField('price', currency='BTC', default='5', max_digits=9,
                           decimal_places=2)
        self.assertEquals(field.get_prep_value(Price(5, currency='BTC')),
                          Decimal(5))

    def test_from_db_value(self):
        field = PriceField('price', currency='BTC', default='5', max_digits=9,
                           decimal_places=2)
        self.assertEqual(
            field.from_db_value(7, None, None, None), Price(7, currency='BTC'))

    def test_from_db_value_handles_none(self):
        field = PriceField('price', currency='BTC', default='5', max_digits=9,
                           decimal_places=2)
        self.assertEqual(field.from_db_value(None, None, None, None), None)

    def test_from_db_value_checks_currency(self):
        field = PriceField('price', currency='BTC', default='5', max_digits=9,
                           decimal_places=2)
        invalid = Price(1, currency='USD')
        self.assertRaises(
            ValueError, lambda: field.from_db_value(invalid, None, None, None))

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
