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
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return xml.sax.saxutils.escape(text)

chapters = '\n'.join(
    [read('src', 'z3c', 'formjs', name)
    for name in ('README.txt',
                 'jsaction.txt',
                 'jsvalidator.txt',
                 'jsevent.txt')])

setup (
    name='z3c.formjs',
    version='0.4.0',
    author = "Paul Carduner and the Zope Community",
    author_email = "zope3-dev@zope.org",
    description = "Javascript integration into ``z3c.form``",
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' + chapters
        + '\n\n' +
        read('CHANGES.txt')
        + '\n\n' +
        read('TODO.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 form javascript",
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
    url = 'http://svn.zope.org/z3c.formjs',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = ['zope.testing', 'zope.app.testing', 'z3c.coverage'],
        docs = ['Sphinx', 'z3c.recipe.sphinxdoc'],
        ),
    install_requires = [
        'jquery.layer',
        'setuptools',
        'z3c.form',
        'z3c.traverser',
        'zope.app.pagetemplate',
        'zope.component',
        'zope.interface',
        'zope.location',
        'zope.publisher',
        'zope.schema',
        'zope.traversing',
        'python-cjson',
        ],
    dependency_links = ['http://download.zope.org/distribution'],
    zip_safe = False,
    )
