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

$Id: setup.py 82497 2007-12-28 14:59:22Z rogerineichen $
"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name = 'z3c.recipe.paster',
    version = '0.5.1',
    author = 'Roger Ineichen and the Zope Community',
    author_email = 'zope-dev@zope.org',
    description = 'Zope3 paste deploy setup recipe',
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n\n' +
        read('src', 'z3c', 'recipe', 'paster', 'README.txt')
        + '\n\n' +
        read('src', 'z3c', 'recipe', 'paster', 'paster.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = 'ZPL 2.1',
    keywords = 'zope zope3 z3c paste deploy recipe',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/z3c.recipe.paster',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c', 'z3c.recipe'],
    extras_require = dict(
        test = [
            'transaction',
            'ZODB3',
            'pytz',
            'zc.lockfile',
            'zc.recipe.filestorage',
            'zdaemon',
            'zope.annotation',
            'zope.app.appsetup',
            'zope.authentication',
            'zope.app.publication',
            'zope.browser',
            'zope.broken',
            'zope.cachedescriptors',
            'zope.component',
            'zope.configuration',
            'zope.container',
            'zope.copy',
            'zope.deferredimport',
            'zope.dottedname',
            'zope.error',
            'zope.event',
            'zope.exceptions',
            'zope.filerepresentation',
            'zope.i18n',
            'zope.i18nmessageid',
            'zope.processlifetime',
            'zope.lifecycleevent',
            'zope.location',
            'zope.minmax',
            'zope.proxy',
            'zope.publisher',
            'zope.session',
            'zope.site',
            'zope.size',
            'zope.testing',
            'zc.buildout',
            'zope.traversing',
            'zope.security',
            ],
        ),
    install_requires = [
        'Paste',
        'PasteDeploy',
        'PasteScript',
        'ZConfig >=2.4a5',
        'setuptools',
        'zc.recipe.egg',
        'zope.app.wsgi',
        'zope.app.debug',
        'zope.schema',
        'zope.interface',
        ],
    entry_points = {
        'zc.buildout': [
             'serve = z3c.recipe.paster.serve:ServeSetup',
             'paster = z3c.recipe.paster.paster:PasterSetup',
             'debug = z3c.recipe.paster.debug:DebugSetup',
         ]
    },
)
