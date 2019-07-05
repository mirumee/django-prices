# coding: utf-8
import functools

import pytest
from django.utils import translation
from django_prices.templatetags import prices
from django_prices.utils.formatting import get_currency_fraction

from prices import Money, TaxedMoney, percentage_discount


@pytest.fixture(scope="module")
def money_fixture():
    return Money("10", "USD")


def test_templatetag_discount_amount_for():
    price = TaxedMoney(Money(30, "BTC"), Money(30, "BTC"))

    discount = functools.partial(percentage_discount, percentage=50)
    discount_amount = prices.discount_amount_for(discount, price)
    assert discount_amount == TaxedMoney(Money(-15, "BTC"), Money(-15, "BTC"))


def test_non_existing_locale(money_fixture):
    # Test detecting an error that occur for language 'zh_CN' for which
    # the canonical code is 'zh_Hans_CN', see:
    #     Babel 1.0+ doesn't support `zh_CN`
    #     https://github.com/python-babel/babel/issues/37
    # Though to make this test more reliable we mock the language with totally
    # made up code 'zz' as the 'zh_CN' "alias" might work in the future, see:
    #     Babel needs to support Fuzzy Locales
    #     https://github.com/python-babel/babel/issues/30
    translation.activate("zz")
    amount = prices.amount(money_fixture, format="html")
    assert amount  # No exception, success!


def test_non_cannonical_locale_zh_CN(money_fixture, settings):
    # Test detecting an error that occur for language 'zh_CN' for which
    # the canonical code is 'zh_Hans_CN', see:
    #     Babel 1.0+ doesn't support `zh_CN`
    #     https://github.com/python-babel/babel/issues/37
    # This should now work, as we are using:
    #     `Locale.parse('zh_CN')`
    # which does the conversion to the canonical name.

    # Making sure the default "LANGUAGE_CODE" is "en_US"
    settings.LANGUAGE_CODE = "en_US"

    # Checking format of the default locale
    amount = prices.amount(money_fixture, format="html")
    assert amount == '<span class="currency">$</span>10.00'

    # Checking if 'zh_CN' has changed the format
    translation.activate("zh_CN")
    amount = prices.amount(money_fixture, format="html")
    assert amount == '<span class="currency">US$</span>10.00'  # 'US' before '$'


def test_templatetag_amount(money_fixture):
    amount = prices.amount(money_fixture)
    assert amount == "$10.00"


def test_templatetag_amount_html(money_fixture):
    amount = prices.amount(money_fixture, format="html")
    assert amount == '<span class="currency">$</span>10.00'


def test_templatetag_amount_wrong_param(money_fixture):
    amount = prices.amount(money_fixture, format="test")
    assert amount == "$10.00"


def test_get_currency_fraction_USD():
    result = get_currency_fraction("USD")
    assert result == 2


def test_get_currency_fraction_unknown_currency():
    result = get_currency_fraction(("test"))
    assert result == 2


def test_format_price_invalid_value():
    result = prices.format_price("invalid", "USD")
    assert result == ""
