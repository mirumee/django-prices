#! /usr/bin/env python
from setuptools import setup

CLASSIFIERS = [
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Software Development :: Libraries :: Python Modules",
]


setup(
    name="django-prices",
    author="Mirumee Software",
    author_email="hello@mirumee.com",
    description="Django fields for the prices module",
    license="BSD",
    version="2.1.0a1",
    url="https://github.com/mirumee/django-prices",
    packages=["django_prices", "django_prices.templatetags"],
    include_package_data=True,
    classifiers=CLASSIFIERS,
    install_requires=["Babel>=2.2", "Django>=1.11,<3", "django-babel", "prices>=1.0.0"],
    platforms=["any"],
    zip_safe=False,
)
