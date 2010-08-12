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

$Id: setup.py 82497 2007-12-28 14:59:22Z rogerineichen $
"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'z3c.recipe.dev',
    version = '0.5.5dev',
    author = 'Roger Ineichen and the Zope Community',
    author_email = 'zope-dev@zope.org',
    description = 'Zope3 development server setup recipes',
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************'
        + '\n\n' +
        read('src', 'z3c', 'recipe', 'dev', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = 'ZPL 2.1',
    keywords = 'zope3 z3c dev recipe',
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
    url = 'http://pypi.python.org/pypi/z3c.recipe.dev',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c', 'z3c.recipe'],
    extras_require = dict(
        test = [
            'zc.recipe.filestorage',
            ],
        ),
    install_requires = [
        'ZConfig >=2.4a5',
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        'zope.testing',
        ],
    entry_points = {
        'zc.buildout': [
             'app = z3c.recipe.dev.app:AppSetup',
             'script = z3c.recipe.dev.script:ScriptSetup',
             'mkdir = z3c.recipe.dev.mkdir:MkdirSetup',
             'mkfile = z3c.recipe.dev.mkfile:MkfileSetup',
         ]
    },
)
