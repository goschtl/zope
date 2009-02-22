##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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

import os
from setuptools import setup, find_packages

#entry_points = """
#[paste.app_factory]
#main = zope.pipeline.entry:create_pipeline
#"""

setup(
    name='zope.pipeline',
    version = '0.1dev',
    url='http://pypi.python.org/pypi/zope.pipeline',
    license='ZPL 2.1',
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    description="Zope object publisher based on a WSGI pipeline",
    long_description=(
        open('README.txt').read()
        + '\n\n'
        + open('CHANGES.txt').read()),

      #entry_points = entry_points,

    packages=find_packages('src'),
    package_dir = {'': 'src'},

    namespace_packages=['zope',],
    install_requires=[
        'setuptools',
        'transaction',
        'ZODB3',
        #'zope.app.security',
        'zope.component',
        'zope.httpform',
        'zope.i18n',
        'zope.interface',
        'zope.publisher',
        'zope.traversing', # for namespace traversal
        'zope.security',
        ],
    extras_require=dict(
        test=[
            'zope.testing',
            'zope.configuration',
            ],
        ),
    include_package_data = True,

    zip_safe = False,
    )
