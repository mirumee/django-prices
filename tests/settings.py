from __future__ import unicode_literals

SECRET_KEY = "irrelevant"

INSTALLED_APPS = ["django_prices", "tests"]

TEMPLATES = [
    {"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}
]

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "database.sqlite"}
}
