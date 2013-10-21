from decimal import Decimal
from unittest import TestCase

from django.db import models
from prices import Price

from .models import PriceField


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
