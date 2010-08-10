##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors
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
    return (
        open(os.path.join(os.path.dirname(__file__), *rnames)).read() +
        '\n\n')

setup (
    name='z3c.objectpolicy',
    version='0.1',
    author = "Zope Foundation and Contributors",
    author_email = "zope-dev@zope.org",
    description = "objectpolicy for Zope3",
    long_description=(
        read('README.txt')+
        '.. contents::\n\n' +
        read('src', 'z3c', 'objectpolicy', 'README.txt') +
        read('src', 'z3c', 'objectpolicy', 'highlevel.txt') +
        read('src', 'z3c', 'objectpolicy', 'lowlevel.txt') +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 z3c objectpolicy",
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
    url = 'http://cheeseshop.python.org/pypi/z3c.objectpolicy',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'z3c.coverage',
            'zope.app.testing',
            'zope.configuration',
            'zope.testing',
            ],
        ),
    install_requires = [
        'setuptools',
        'zope.component',
        'zope.interface',
        'zope.securitypolicy',
        'zope.app.security',
        ],
    zip_safe = False,
)
