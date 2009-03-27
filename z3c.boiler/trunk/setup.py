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
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    text = unicode(text, 'utf-8').encode('ascii', 'xmlcharrefreplace')
    return text

setup (
    name='z3c.boiler',
    version='0.2.0dev',
    author = "Paul Carduner, Stephan Richter, and hopefully others...",
    author_email = "zope-dev@zope.org",
    description = "A utility to help jump start Zope 3 projects",
    long_description=(
        read('README.txt') +
        "\n\n" +
        "Detailed Documentation\n" +
        "**********************\n" +
        "\n\n" +
        read('src', 'z3c', 'boiler', 'README.txt') +
        "\n\n" +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 project builder boiler",
    url = 'http://pypi.python.org/pypi/z3c.boiler',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'zope.testing',
            'z3c.coverage',
            ],
        docs = ['Sphinx',
                'z3c.recipe.sphinxdoc'],
        deps = ['gtkeggdeps'],
        ),
    install_requires = [
        'setuptools',
        'zc.buildout',
        'z3c.builder.core',
        'z3c.feature.core',
        'z3c.feature.zope',
        ],
    zip_safe = False,
    entry_points = """
    [console_scripts]
    boil = z3c.boiler.script:main
    """,
    )
