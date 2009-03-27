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
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    text = unicode(text, 'utf-8').encode('ascii', 'xmlcharrefreplace')
    return xml.sax.saxutils.escape(text)

setup (
    name='z3c.builder.core',
    version='0.1.0',
    author = "Paul Carduner, Stephan Richter, and hopefully others...",
    author_email = "zope-dev@zope.org",
    description = "A utility to help jump start Zope 3 projects",
    long_description=(
        read('README.txt')
        +"\n\n"+
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 project builder",
    url = 'http://pypi.python.org/pypi/z3c.builder.core',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'zope.testing',
            'z3c.coverage',
            ],
        docs = ['Sphinx'],
        ),
    install_requires = [
        'rwproperty',
        'setuptools',
        'zc.buildout',
        'zope.component',
        'zope.configuration',
        'zope.container',
        'zope.interface',
        'zope.schema',
        'lxml',
        ],
    zip_safe = False,
    )
