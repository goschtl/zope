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

$Id: setup.py 79209 2007-08-24 03:50:29Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='z3c.skin.pagelet',
    version='1.4.0',
    author = "Stephan Richter, Roger Ineichen and the Zope Community",
    author_email = "zope3-dev@zope.org",
    description = "The z3c pagelet implementation",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 pagelet",
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
    url = 'http://cheeseshop.python.org/pypi/z3c.skin.pagelet',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c', 'z3c.skin'],
    extras_require = dict(
        app = ['zope.app.component',
               'zope.app.pagetemplate',
               'zope.app.publisher',
               'zope.app.publication',
               'zope.app.container',
               'zope.app.testing',
               'zope.app.zapi',
               'zope.contentprovider',
               'zope.i18n',
               'zope.i18nmessageid',
               'zope.interface',
               'zope.schema',
               'zope.security',
               'zope.testing',
               'zope.traversing',
               'zope.viewlet',
               ],
        test = ['z3c.coverage',
                'z3c.etestbrowser',
                'zope.app.testing'],
        ),
    install_requires = [
        'setuptools',
        'zope.app.component',
        'zope.app.pagetemplate',
        'zope.app.publisher',
        'zope.app.container',
        'zope.app.securitypolicy',
        'zope.app.testing',
        'zope.app.twisted',
        'zope.app.zapi',
        'zope.contentprovider',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
        'zope.security',
        'zope.testing',
        'zope.traversing',
        'zope.viewlet',
        'z3c.i18n',
        'z3c.layer',
        'z3c.macro',
        'z3c.macroviewlet',
        'z3c.menu',
        'z3c.pagelet',
        'z3c.template',
        'z3c.viewlet',
        'z3c.zrtresource',
        ],
    dependency_links = ['http://download.zope.org/distribution'],
    zip_safe = False,
    )
