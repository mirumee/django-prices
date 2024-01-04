#! /usr/bin/env python
from setuptools import setup

CLASSIFIERS = [
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setup(
    name="django-prices",
    author="dmazoli",
    author_email="d.m.piccoli@gmail.com",
    description="Django fields for the prices module updated, forked from https://github.com/mirumee/django-prices",
    license="BSD",
    version="2.3.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dmazoli/django-prices-2024",
    packages=["django_prices", "django_prices.templatetags", "django_prices.utils"],
    include_package_data=True,
    classifiers=CLASSIFIERS,
    install_requires=[
        "Babel>=2.2",
        "Django>=3.0,<6",
        "enmerkar>=0.7.1",
        "prices>=1.0.0",
    ],
    platforms=["any"],
    zip_safe=False,
)
