##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Setup

$Id$
"""
from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'zope.app.sqlexpr',
    version = '0.2dev',
    author = 'Stephan Richter and the Zope Community',
    author_email = 'zope-dev@zope.org',
    description = 'allow quick SQL queries in TALES expressions and Zope Page Templates',
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************\n\n' +
        read('CHANGES.txt')
        ),
    license = 'ZPL 2.1',
    keywords = "zope3 sql zpt tales",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],

    url = 'http://pypi.python.org/pypi/zope.app.sqlexpr',
    include_package_data = True,
    packages = find_packages('src'),
    namespace_packages = ['zope', 'zope.app'],
    package_dir = {'': 'src'},
    install_requires = ['setuptools',
                        'zope.component',
                        'zope.interface',
                        'zope.tales',
                        'zope.exceptions',
                        'zope.rdb'],
    extras_require=dict(test=['zope.app.sqlexpr']),
    zip_safe = False,
    )
