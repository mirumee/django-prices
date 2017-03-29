# coding: utf-8
from __future__ import unicode_literals

from decimal import Decimal

import pytest
from django.db import connection
from django.utils import translation
from django_prices import forms, widgets
from django_prices.models import PriceField
from django_prices.templatetags import prices as tags
from django_prices.templatetags import prices_i18n
from prices import Price, percentage_discount

from .forms import ModelForm, OptionalPriceForm, RequiredPriceForm
from .models import Model


@pytest.fixture(scope='module')
def price_fixture():
    return Price(net='10', gross='15', currency='USD')


@pytest.fixture(scope='module')
def price_with_decimals():
    return Price(net='10.20', gross='15', currency='USD')


def test_init():
    field = PriceField(
        currency='BTC', default='5', max_digits=9, decimal_places=2)
    assert field.get_default() == Price(5, currency='BTC')


def test_get_prep_value():
    field = PriceField('price', currency='BTC', default='5', max_digits=9,
                       decimal_places=2)
    assert field.get_prep_value(Price(5, currency='BTC')) == Decimal(5)


def test_get_db_prep_save():
    field = PriceField('price', currency='BTC', default='5', max_digits=9,
                       decimal_places=2)
    value = field.get_db_prep_save(Price(5, currency='BTC'), connection)
    assert value == '5.00'


def test_value_to_string():
    instance = Model(price=30)
    field = instance._meta.get_field('price')
    assert field.value_to_string(instance) == Decimal('30')


def test_from_db_value():
    field = PriceField('price', currency='BTC', default='5', max_digits=9,
                       decimal_places=2)
    assert field.from_db_value(7, None, None, None) == Price(7, currency='BTC')


def test_from_db_value_handles_none():
    field = PriceField('price', currency='BTC', default='5', max_digits=9,
                       decimal_places=2)
    assert field.from_db_value(None, None, None, None) is None


def test_from_db_value_checks_currency():
    field = PriceField('price', currency='BTC', default='5', max_digits=9,
                       decimal_places=2)
    invalid = Price(1, currency='USD')
    with pytest.raises(ValueError):
        field.from_db_value(invalid, None, None, None)


def test_formfield():
    field = PriceField('price', currency='BTC', default='5', max_digits=9,
                       decimal_places=2)
    form_field = field.formfield()
    assert isinstance(form_field, forms.PriceField)
    assert form_field.currency == 'BTC'
    assert isinstance(form_field.widget, widgets.PriceInput)


@pytest.mark.parametrize("data,initial,expected_result", [
    ('5', Price(5, currency='BTC'), False),
    ('5', Price(10, currency='BTC'), True),
    ('5', '5', False),
    ('5', '10', True),
    ('5', None, True),
    (None, Price(5, currency='BTC'), True),
    (None, '5', True),
    (None, None, False)])
def test_form_changed_data(data, initial, expected_result):
    form = RequiredPriceForm(
        data={'price': data}, initial={'price': initial})
    assert bool(form.changed_data) == expected_result


def test_render():
    widget = widgets.PriceInput('BTC', attrs={'type': 'number'})
    result = widget.render('price', 5, attrs={'foo': 'bar'})
    attrs = [
        'foo="bar"', 'name="price"', 'type="number"', 'value="5"', 'BTC']
    for attr in attrs:
        assert attr in result


def test_instance_values():
    instance = Model(price=25)
    assert instance.price.net == 25


def test_field_passes_all_validations():
    form = RequiredPriceForm(data={'price': '20'})
    form.full_clean()
    assert form.errors == {}


def test_model_field_passes_all_validations():
    form = ModelForm(data={'price': '20'})
    form.full_clean()
    assert form.errors == {}


def test_field_passes_none_validation():
    form = OptionalPriceForm(data={'price': None})
    form.full_clean()
    assert form.errors == {}


def test_templatetag_i18n_gross(price_fixture):
    gross = prices_i18n.gross(price_fixture)
    assert gross == '$15.00'


def test_templatetag_i18n_gross_html(price_fixture):
    gross = prices_i18n.gross(price_fixture, html=True)
    assert gross == '<span class="currency">$</span>15.00'


def test_templatetag_i18n_gross_normalize(price_fixture):
    gross = prices_i18n.gross(price_fixture, normalize=True)
    assert gross == '$15'


def test_templatetag_i18n_gross_html_normalize(price_fixture):
    gross = prices_i18n.gross(price_fixture, html=True, normalize=True)
    assert gross == '<span class="currency">$</span>15'


def test_templatetag_i18n_net(price_fixture):
    net = prices_i18n.net(price_fixture)
    assert net == '$10.00'


def test_templatetag_i18n_net_html(price_fixture):
    net = prices_i18n.net(price_fixture, html=True)
    assert net == '<span class="currency">$</span>10.00'


def test_templatetag_i18n_net_html_normalize(price_fixture):
    net = prices_i18n.net(price_fixture, html=True, normalize=True)
    assert net == '<span class="currency">$</span>10'


def test_templatetag_i18n_net_normalize(price_fixture):
    net = prices_i18n.net(price_fixture, normalize=True)
    assert net == '$10'


def test_templatetag_i18n_net_normalize_with_decimals():
    price = Price(net='12.23', currency='USD')
    net = prices_i18n.net(price, normalize=True)
    assert net == '$12.23'


def test_templatetag_i18n_tax(price_fixture):
    tax = prices_i18n.tax(price_fixture)
    assert tax == '$5.00'


def test_templatetag_i18n_tax_html(price_fixture):
    tax = prices_i18n.tax(price_fixture, html=True)
    assert tax == '<span class="currency">$</span>5.00'


def test_templatetag_i18n_tax_normalize(price_fixture):
    tax = prices_i18n.tax(price_fixture, normalize=True)
    assert tax == '$5'


def test_templatetag_i18n_tax_html_normalize(price_fixture):
    tax = prices_i18n.tax(price_fixture, html=True, normalize=True)
    assert tax == '<span class="currency">$</span>5'


def test_templatetag_discount_amount_for():
    price = Price(30, currency='BTC')
    discount = percentage_discount(50)
    discount_amount = tags.discount_amount_for(discount, price)
    assert discount_amount == Price(-15, currency='BTC')


def test_non_existing_locale(price_fixture):
    # Test detecting an error that occur for language 'zh_CN' for which
    # the canonical code is 'zh_Hans_CN', see:
    #     Babel 1.0+ doesn't support `zh_CN`
    #     https://github.com/python-babel/babel/issues/37
    # Though to make this test more reliable we mock the language with totally
    # made up code 'oO_Oo' as the 'zh_CN' "alias" might work in the future, see:
    #     Babel needs to support Fuzzy Locales
    #     https://github.com/python-babel/babel/issues/30
    translation.activate('oO_Oo')
    tax = prices_i18n.tax(price_fixture, html=True)
    assert tax  # No exception, success!


def test_non_cannonical_locale_zh_CN(price_fixture, settings):
    # Test detecting an error that occur for language 'zh_CN' for which
    # the canonical code is 'zh_Hans_CN', see:
    #     Babel 1.0+ doesn't support `zh_CN`
    #     https://github.com/python-babel/babel/issues/37
    # This should now work, as we are using:
    #     `Locale.parse('zh_CN')`
    # which does the conversion to the canonical name.

    # Making sure the default "LANGUAGE_CODE" is "en_US"
    settings.LANGUAGE_CODE = 'en_US'

    # Checking format of the default locale
    tax = prices_i18n.tax(price_fixture, html=True)
    assert tax == '<span class="currency">$</span>5.00'

    # Checking if 'zh_CN' has changed the format
    translation.activate('zh_CN')
    tax = prices_i18n.tax(price_fixture, html=True)
    assert tax == '<span class="currency">US$</span>5.00'  # 'US' before '$'


@pytest.mark.parametrize('value, normalize, expected',
                         [(Decimal('12.00'), True, Decimal('12')),
                          (Decimal('12.00'), False, Decimal('12.00')),
                          (Decimal('12.23'), True, Decimal('12.23'))])
def test_normalize_price(value, normalize, expected):
    assert tags.normalize_price(value, normalize) == expected


@pytest.mark.parametrize('value, expected',
                         [(Decimal('12'), '12'),
                          (Decimal('12.20'), '12.2'),
                          (Decimal('1222'), '1,222'),
                          (Decimal('12.23'), '12.23')])
def test_format_normalize_price(value, expected):
    formatted_price = prices_i18n.format_price(value, 'USD', normalize=True)
    assert formatted_price == '$%s' % expected


def test_format_normalize_price_no_digits():
    formatted_price = prices_i18n.format_price(123, 'JPY', normalize=True)
    assert formatted_price == '¥123'


@pytest.mark.parametrize(
    'value,expected', [(123.002, 'BHD123.002'), (123.000, 'BHD123')])
def test_format_normalize_price_three_digits(value, expected):
    normalized_price = prices_i18n.format_price(value, 'BHD', normalize=True)
    assert normalized_price == expected


@pytest.mark.parametrize('value', [Decimal('12.22'), Decimal('1222.22')])
def test_normalize_same_as_formatted(value):
    formatted_price = prices_i18n.format_price(value, 'USD', normalize=True)
    assert formatted_price == prices_i18n.net(Price(net=value, currency='USD'))


@pytest.mark.parametrize('value', [Decimal('12'), Decimal('1222')])
def test_normalize_same_as_formatted(value):
    formatted_price = prices_i18n.format_price(value, 'USD', normalize=True)
    net = prices_i18n.net(Price(net=value, currency='USD'))
    assert not formatted_price == net


def test_templatetag_gross(price_fixture):
    gross = tags.gross(price_fixture)
    assert gross['amount'] == Decimal('15')
    assert gross['currency'] == price_fixture.currency


def test_templatetag_net(price_fixture):
    net = tags.net(price_fixture)
    assert net['amount'] == Decimal('10')
    assert net['currency'] == price_fixture.currency


def test_templatetag_tax(price_fixture):
    tax = tags.tax(price_fixture)
    assert tax['amount'] == Decimal('5')
    assert tax['currency'] == price_fixture.currency


def test_templatetag_net_normalize_one_point(price_with_decimals):
    net = tags.net(price_with_decimals, normalize=True)
    assert str(net['amount']) == '10.20'


def test_templatetag_i18n_tax_normalize_one_digit(price_with_decimals):
    tax = prices_i18n.tax(price_with_decimals, normalize=True)
    assert tax == '$4.80'
