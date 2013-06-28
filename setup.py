#! /usr/bin/env python
from setuptools import setup

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules']

setup(name='django-prices',
      author='Mirumee Software',
      author_email='hello@mirumee.com',
      description='Django fields for the prices module',
      license='BSD',
      version='0.2.2',
      url='http://satchless.com/',
      packages=['django_prices', 'django_prices.templatetags'],
      include_package_data=True,
      classifiers=CLASSIFIERS,
      install_requires=['django', 'prices >= 0.4, < 0.5a0'],
      platforms=['any'],
      zip_safe=False)
