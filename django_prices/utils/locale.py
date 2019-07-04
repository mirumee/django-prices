from babel.core import Locale, UnknownLocaleError
from django.conf import settings
from django.utils.translation import get_language, to_locale


def get_locale_data():
    language = get_language()
    if not language:
        language = settings.LANGUAGE_CODE
    locale_code = to_locale(language)
    locale = None
    try:
        locale = Locale.parse(locale_code)
    except (ValueError, UnknownLocaleError):
        # Invalid format or unknown locale
        # Fallback to the default language
        language = settings.LANGUAGE_CODE
        locale_code = to_locale(language)
        locale = Locale.parse(locale_code)
    return locale, locale_code
