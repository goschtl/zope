# CMF packaged as an egg
__version__ = '2.1.0.0'

from ez_setup import use_setuptools
use_setuptools()

import os

from setuptools import setup, find_packages

here = os.path.dirname(__file__)
README = open(os.path.join(here, 'README.txt')).read()

setup(
    name='cmflib',
    version='2.1.0.0',
    description='Zope CMF Product libraries',
    long_description=README,
    keywords='web application server cmf zope',
    author='Zope Corporation and Contributors',
    author_email='zope@zope.org',
    url='http://www.zope.org',
    license='ZPL 2.1',
    packages=find_packages(),
    include_package_data=True,
    namespace_packages=['Products'],
    install_requires = ['Products.GenericSetup == 1.3.2'],
    zip_safe=False,
    )
