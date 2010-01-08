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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.app.zptpage package

$Id$
"""

import os

from setuptools import setup, find_packages, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='zope.app.zptpage',
    version = '3.5.1',
    url='http://pypi.python.org/pypi/zope.app.zptpage',
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    license='ZPL 2.1',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Framework :: Zope3',
        ],
    description='ZPT page content component',
    long_description = (
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zope', 'zope.app'],
    include_package_data=True,
    install_requires=['setuptools',
                      'zope.container',
                      'zope.app.publication',
                      'zope.filerepresentation',
                      'zope.formlib',
                      'zope.i18nmessageid',
                      'zope.index',
                      'zope.interface',
                      'zope.pagetemplate',
                      'zope.publisher >= 3.12',
                      'zope.schema',
                      'zope.security',
                      'zope.site',
                      'zope.size',
                      'zope.traversing',
                      'ZODB3',
                      ],
    extras_require=dict(test=['zope.app.testing',
                              'zope.app.securitypolicy',
                              'zope.app.zcmlfiles',
                              'zope.login',
                              # The tests expect a spec-compliant TAL
                              # interpreter as found in zope.tal 3.5.0:
                              'zope.tal >= 3.5.0',
                              ]),
    zip_safe=False,
    )
