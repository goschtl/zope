##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Setup for z3c.mvc package

$Id$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='z3c.mvc',
    version = '0.1.0',
    description='Strict Model-View-Controller implementation',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['z3c'],
    extras_require=dict(
        test=['zope.app.testing',
              'zope.testing',
              'zope.app.securitypolicy',
              'zope.app.zcmlfiles']),
    install_requires=[
        'setuptools',
        'z3c.pagelet',
        'z3c.template',
        'zope.interface',
        'zope.component',
        'zope.app.pagetemplate',
        'zope.configuration',
        'zope.publisher',
        ],
    include_package_data = True,
    zip_safe = False,
    )
