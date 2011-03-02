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
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='zc.comment',
    version='0.2.0dev',
    author = "Zope Community",
    author_email = "zope-dev@zope.org",
    description = "A simple comment package.",
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************'
        + '\n\n' +
        read('src', 'zc', 'comment', 'README.txt')
        + '\n\n' +
        read('src', 'zc', 'comment', 'browser', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 comment",
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
    url = 'http://pypi.python.org/pypi/zc.comment',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = ['setuptools',
                        'zope.interface >= 3.3',
                        'zope.component',
                        'zope.schema >= 3.6',
                        'zope.cachedescriptors',
                        'zope.app.zapi',
                        'zope.app.pagetemplate',
                        'zope.annotation',
                        'zope.lifecycleevent',
                        'zope.i18nmessageid',
                        'zope.event',
                        'zope.publisher',
                        'zope.security',
                        'ZODB3',
                        'pytz',
                        ],
    extras_require = dict(
        test=['zope.app.testing',
              'zope.app.zcmlfiles',
              'zope.testbrowser',
              'zope.testing',
              ],
        browser=['zope.formlib',
                 'zc.table >= 0.7',
                 'zope.app.form'
                 ],
        ),
    zip_safe = False,
    )
