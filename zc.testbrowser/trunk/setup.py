##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os
from setuptools import setup, find_packages

long_description = (
    open('README.txt').read()
    + open('CHANGES.txt').read()
    + '.. contents::\n\n\n'
    + open(os.path.join('src', 'zc', 'testbrowser', 'README.txt')).read()
    )

setup(
    name = 'zc.testbrowser',
    version = '1.0.0a6dev',
    url = 'http://pypi.python.org/pypi/zc.testbrowser',
    license = 'ZPL 2.1',
    description = 'Programmable web browser for functional black-box testing '
                  'of web applications',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope3-dev@zope.org',
    long_description = long_description,
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Topic :: Internet :: WWW/HTTP',
        ],

    packages = find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['zc',],
    tests_require = ['zope.testing'],
    install_requires = [
        'ClientForm',
        'mechanize',
        'setuptools',
        'simplejson',
        'zope.interface',
        'zope.schema',
        ],

    include_package_data = True,
    zip_safe = False,
    )
