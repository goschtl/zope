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
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='z3c.website',
    version='0.1.0c1',
    author = "Roger Ineichen and the Zope Community",
    author_email = "zope-dev@zope.org",
    description = "Source code for Z3C Website",
    long_description=(
        read('README.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 z3c website",
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
    url = 'http://svn.zope.org/z3c.website',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        app = ['zope.app.appsetup',
               'zope.app.authentication',
               'zope.app.component',
               'zope.app.container',
               'zope.app.error',
               'zope.app.form',
               'zope.app.publisher',
               'zope.app.publication',
               'zope.app.security',
               'zope.app.securitypolicy',
               'zope.app.twisted',
               'zope.app.wsgi',
               'zope.contentprovider',
               ],
        ),
    install_requires = [
        'jquery.javascript',
        'jquery.jsonform',
        'jquery.layer',
        'jquery.widget',
        'setuptools',
        'z3c.csvvocabulary',
        'z3c.form',
        'z3c.formui',
        'z3c.formdemo',
        'z3c.layer',
        'z3c.pagelet',
        'z3c.template',
        'z3c.viewlet',
        'z3c.zrtresource',
        'zc.resourcelibrary',
        'zc.table',
        'zope.annotation',
        'zope.app.container',
        'zope.app.pagetemplate',
        'zope.app.session',
        'zope.component',
        'zope.interface',
        'zope.location',
        'zope.pagetemplate',
        'zope.publisher',
        'zope.schema',
        'zope.traversing',
        'zope.viewlet',
        ],
    zip_safe = False,
    )
