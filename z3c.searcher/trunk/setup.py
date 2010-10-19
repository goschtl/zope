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

$Id:$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='z3c.searcher',
    version='0.6.1dev',
    author = "Roger Ineichen and the Zope Community",
    author_email = "zope-dev@zope.org",
    description = "Persistent and session based search form for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n\n' +
        read('src', 'z3c', 'searcher', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),

    license = "ZPL 2.1",
    keywords = "zope3 z3c catalog index indexer search searcher",
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
    url = 'http://pypi.python.org/pypi/z3c.searcher',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c',],
    extras_require = dict(
        test = [
            'z3c.form [test]',
            'z3c.macro',
            'z3c.testing',
            'zope.app.authentication',
            'zope.app.pagetemplate',
            'zope.app.testing',
            'zope.contentprovider',
            'zope.intid',
            'zope.keyreference',
            'zope.publisher',
            'zope.session',
            'zope.testing',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.form',
        'z3c.formui',
        'z3c.indexer',
        'z3c.template',
        'z3c.table',
        'zope.container',
        'zope.component',
        'zope.event',
        'zope.index',
        'zope.interface',
        'zope.location',
        'zope.schema',
        'zope.session',
        ],
    zip_safe = False,
)
