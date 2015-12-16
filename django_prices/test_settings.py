import os

PROJECT_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'django_prices'))
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(PROJECT_ROOT, 'templates')]}]

SECRET_KEY = 'irrelevant'

INSTALLED_APPS = ['django_prices']
