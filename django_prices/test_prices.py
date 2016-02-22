from decimal import Decimal

from django import forms as django_forms
from django.db import connection, models
from django.utils import translation
from prices import percentage_discount, Price
import pytest

from . import forms
from . import widgets
from .models import PriceField
from .templatetags import prices as tags, prices_i18n


@pytest.fixture(scope='module')
def test_model():
    class TestModel(models.Model):
        price = PriceField(currency='BTC', default='5', max_digits=9,
                           decimal_places=2)
    return TestModel


@pytest.fixture(scope='module')
def price_fixture():
    return Price(net='10', gross='15', currency='USD')


@pytest.fixture(scope='module')
def test_form():
    class PriceForm(django_forms.Form):
        price = forms.PriceField(currency='BTC')
    return PriceForm


@pytest.fixture(scope='module')
def test_model_form(test_model):
    class PriceForm(django_forms.ModelForm):
        class Meta:
            model = test_model
            fields = ['price']
    return PriceForm


@pytest.fixture(scope='module')
def test_form_price_not_required():
    class PriceForm(django_forms.Form):
        price = forms.PriceField(currency='BTC', required=False)
    return PriceForm


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


def test_value_to_string(test_model):
    instance = test_model(price=30)
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
    (None, None, False)
])
def test_form_changed_data(test_form, data, initial, expected_result):
    form = test_form(data={'price': data}, initial={'price': initial})
    assert bool(form.changed_data) == expected_result


def test_render():
    widget = widgets.PriceInput('BTC', attrs={'type': 'number'})
    result = widget.render('price', 5, attrs={'foo': 'bar'})
    attrs = [
        'foo="bar"', 'name="price"', 'type="number"', 'value="5"', 'BTC']
    for attr in attrs:
        assert attr in result


def test_instance_values(test_model):
    instance = test_model(price=25)
    assert instance.price.net == 25


def test_field_passes_all_validations(test_form):
    form = test_form(data={'price': '20'})
    form.full_clean()
    assert form.errors == {}


def test_model_field_passes_all_validations(test_model_form):
    form = test_model_form(data={'price': '20'})
    form.full_clean()
    assert form.errors == {}


def test_field_passes_none_validation(test_form_price_not_required):
    form = test_form_price_not_required(data={'price': None})
    form.full_clean()
    assert form.errors == {}


def test_templatetag_gross(price_fixture):
        gross = prices_i18n.gross(price_fixture)
        assert gross == '$15.00'


def test_templatetag_gross_html(price_fixture):
    gross = prices_i18n.gross(price_fixture, html=True)
    assert gross == '<span class="currency">$</span>15.00'


def test_templatetag_net(price_fixture):
    net = prices_i18n.net(price_fixture)
    assert net == '$10.00'


def test_templatetag_net_html(price_fixture):
    net = prices_i18n.net(price_fixture, html=True)
    assert net == '<span class="currency">$</span>10.00'


def test_templatetag_tax(price_fixture):
    tax = prices_i18n.tax(price_fixture)
    assert tax == '$5.00'


def test_templatetag_tax_html(price_fixture):
    tax = prices_i18n.tax(price_fixture, html=True)
    assert tax == '<span class="currency">$</span>5.00'


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
