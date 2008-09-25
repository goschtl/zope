##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Setup for localy.session package

$Id$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='lovely.session',
    version = '0.2.0',
    author = "Lovely Systems GmbH",
    author_email = "office@lovelysystems.com",
    description = "memcache-based session storage",
    long_description=(
        read('src', 'lovely', 'session', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        + '\n\n' +
        '========\n'
        'Download\n'
        '========\n'
        ),
    license='ZPL 2.1',
    keywords = "zope3 session memcache",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Zope3'],
    url='http://pypi.python.org/pypi/lovely.session',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['lovely',],
    extras_require = dict(
        test = ['zope.app.testing',
                'zope.interface',
                'zope.security',
                'zope.testing',]),
    install_requires = [
        'setuptools',
        'lovely.memcached',
        'zope.app.container',
        'zope.session',
        'zope.schema',
        ],
    extras_require = dict(
        test=['zope.app.testing',
              'zope.app.zptpage',
              'zope.app.securitypolicy',
              'zope.app.zcmlfiles']),
    include_package_data = True,
    zip_safe = False,
    )
