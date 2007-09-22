#!python
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
from setuptools import setup, find_packages

setup(
    name = 'z3c.layer.pagelet',
    version = '0.3.0',
    author = "Zope Community",
    author_email = "zope3-dev@zope.org",
    description = open("README.txt").read(),
    license = "ZPL 2.1",
    keywords = "pagelet layer zope zope3",
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
    url = 'http://svn.zope.org/z3c.layer.pagelet',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'zope.testbrowser',
            'zope.app.securitypolicy',
            'zope.app.testing',
            'zope.app.zcmlfiles',
            'z3c.pagelet',
            ],
        ),
    install_requires = [
        'setuptools',
        'zope.configuration',
        'zope.traversing',
        'zope.app.http',
        'zope.app.publisher',
        ],
    dependency_links = ['http://download.zope.org/distribution'],
    zip_safe = False,
)

