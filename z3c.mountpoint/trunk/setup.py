##############################################################################
#
# Copyright (c) 2007-2009 Zope Foundation and Contributors.
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
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1dev'

setup(
    name='z3c.mountpoint',
    version=version,
    author = "Stephan Richter and the Zope Community",
    author_email = "zope-dev@zope.org",
    description = (
        "Very simple implementation of a mount point for an object in "
        "another ZODB connection."),
    long_description=(
        read('src', 'z3c', 'mountpoint', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 zodb mount mountpoint",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/z3c.mountpoint',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'zope.app.testing',
            'zope.app.publication',
                # 'zope.testing',
                # 'zope.traversing',
                # 'lxml>=2.1.1',
                # 'z3c.pt>=1.0b4',
                # 'z3c.ptcompat',
                # 'zope.app.security',
                # 'zope.formlib',
                ],
        ),
    install_requires = [
        'setuptools',
        # 'z3c.template>=1.2.0',
        # 'z3c.ptcompat',
        #  # TODO: this is only needed for ZCML directives, so can copy
        # 'zope.app.publisher', # things we use from there and get rid of the dependencies.
        'zope.component',
        'zope.app.container',
        # 'zope.configuration',
        # 'zope.contentprovider',
        # 'zope.interface',
        # 'zope.publisher',
        # 'zope.schema',
        # 'zope.security',
        ],
    include_package_data = True,
    zip_safe = False,
    )
