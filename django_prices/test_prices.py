from decimal import Decimal
from unittest import TestCase

import django
from django import forms as django_forms
from django.db import models
from prices import Price
import pytest
from . import forms
from . import widgets
from .models import PriceField


@pytest.fixture(scope='module')
def django_setup():
    django.setup()


@pytest.fixture(scope='module')
def test_model(django_setup):
    class TestModel(models.Model):
        price = PriceField(currency='BTC', default='5', max_digits=9,
                           decimal_places=2)
    return TestModel


@pytest.fixture(scope='module')
def test_form(django_setup):
    class PriceForm(django_forms.Form):
        price = forms.PriceField(currency='BTC')
    return PriceForm


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


@pytest.mark.parametrize("data,initial,expected_result", [
    ('5', Price(5, currency='BTC'), False),
    ('5', Price(10, currency='BTC'), True),
    ('5', '5', False),
    ('5', '10', True),
    ('5', None, True),
    (None, Price(5, currency='BTC'), True),
    (None, '5', True),
    (None, None, False)
])
def test_form_changed_data(test_form, data, initial, expected_result):
    form = test_form(data={'price': data}, initial={'price': initial})
    assert bool(form.changed_data) == expected_result


def test_render(django_setup):
    widget = widgets.PriceInput('BTC', attrs={'type': 'number'})
    result = widget.render('price', 5, attrs={'foo': 'bar'})
    assert (result ==
            '<input foo="bar" name="price" type="number" value="5" /> BTC')


def test_instance_values(test_model):
    instance = test_model(price=25)
    assert instance.price.net == 25
