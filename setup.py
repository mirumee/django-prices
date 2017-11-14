#! /usr/bin/env python
from setuptools import setup

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules']


setup(
    name='django-prices',
    author='Mirumee Software',
    author_email='hello@mirumee.com',
    description='Django fields for the prices module',
    license='BSD',
    version='0.7.0',
    url='https://github.com/mirumee/django-prices',
    packages=['django_prices', 'django_prices.templatetags'],
    include_package_data=True,
    classifiers=CLASSIFIERS,
    install_requires=[
        'Babel>=2.2', 'Django>=1.11', 'django-babel', 'prices>=0.5.7,<0.6a0'],
    platforms=['any'],
    zip_safe=False)
