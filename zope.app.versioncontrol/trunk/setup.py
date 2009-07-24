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

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'zope.app.versioncontrol',
    version = '0.2dev',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = 'a framework for managing multiple versions of objects within a ZODB database.',
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************\n\n' +
        read('CHANGES.txt')
        ),
    license = 'ZPL 2.1',
    keywords = "zope3 zodb versions",
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

    url = 'http://pypi.python.org/pypi/zope.app.versioncontrol',
    packages = find_packages('src'),
    namespace_packages = ['zope', 'zope.app'],
    package_dir = {'': 'src'},
    extras_require=dict(test=['zope.event',
                              'zope.traversing',
                              'zope.annotation',
                              'zope.component']),
    install_requires = ['setuptools',
                        'ZODB3',
                        'zope.datetime',
                        'zope.location',
                        'zope.security'],
    zip_safe = False,
    )
