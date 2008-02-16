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
    name='zamplugin.sampledata',
    version='0.5.0',
    author = "Roger Ineichen and the Zope Community",
    author_email = "zope3-dev@zope.org",
    description = "Sampledata management views Zope Application Management",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 sampledata manager views",
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
    url = 'http://cheeseshop.python.org/pypi/zamplugin.sampledata',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zamplugin'],
    extras_require = dict(
        test = [
            'z3c.coverage',
            'z3c.testing',
            'zope.app.testing',
            'zope.testbrowser',
            ],
        app = [
            'zope.app.appsetup',
            'zope.app.authentication',
            'zope.app.component',
            'zope.app.keyreference',
            'zope.app.publication',
            'zope.app.schema',
            'zope.i18n',
            'zope.publisher',
            'zope.schema',
            'zope.security',
            'zope.securitypolicy',
            'zope.session',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.baseregistry',
        'z3c.form',
        'z3c.formui',
        'z3c.menu.ready2go',
        'z3c.pagelet',
        'z3c.sampledata',
        'z3c.template',
        'zam.api',
        'zam.skin',
        'zope.component',
        'zope.exceptions',
        'zope.interface',
        'zope.schema',
        'zope.traversing',
        ],
    zip_safe = False,
)
