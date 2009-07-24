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
"""
$Id$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='lovely.tag',
    version='1.0.0',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    description = "A tagging engine for Zope 3",
    long_description=(
        read('src', 'lovely', 'tag', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 lovely tag cloud",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/lovely.tag',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely'],
    extras_require = dict(
        test = ['zope.app.testing',
                'zope.app.catalog',
                'zope.keyreference',
                'z3c.sampledata']
        ),
    install_requires = [
        'setuptools',
        'ZODB3',
        'pytz',
        'z3c.configurator',
        'zope.app.component',
        'zope.app.container',
        'zope.app.folder',
        'zope.app.generations',
        'zope.app.intid',
        'zope.app.pagetemplate',
        'zope.app.zopeappgenerations',
        'zope.cachedescriptors',
        'zope.component',
        'zope.dottedname',
        'zope.formlib',
        'zope.i18nmessageid',
        'zope.index',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.schema',
        'zope.security'
        ],
    zip_safe = False,
)
