#! /usr/bin/env python
import os
from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_prices.test_settings')

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules']


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]
    test_args = []

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name='django-prices',
    author='Mirumee Software',
    author_email='hello@mirumee.com',
    description='Django fields for the prices module',
    license='BSD',
    version='0.4.8',
    url='https://github.com/mirumee/django-prices',
    packages=['django_prices', 'django_prices.templatetags'],
    include_package_data=True,
    classifiers=CLASSIFIERS,
    install_requires=['BabelDjango', 'django', 'prices>=0.5,<0.6a0'],
    tests_require=['pytest'],
    platforms=['any'],
    test_suite='django_prices.tests',
    cmdclass={
        'test': PyTest},
    zip_safe=False)
