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
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='z3c.skin.ready2go',
    version='0.5.0',
    author = "Stephan Richter, Roger Ineichen and the Zope Community",
    author_email = "zope3-dev@zope.org",
    description = "A ready to go skin for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 z3c ready 2 go skin",
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
    url = 'http://cheeseshop.python.org/pypi/z3c.skin.ready2go',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c', 'z3c.skin'],
    extras_require = dict(
        test = [
            'z3c.coverage',
            'z3c.etestbrowser',
            'zope.app.testing',
            'zope.app.securitypolicy',
            ],
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
        'z3c.layer.pagelet',
        'z3c.layer.ready2go',
        'z3c.menu.ready2go',
        'zc.configuration',
        ],
    zip_safe = False,
)