##############################################################################
#
# Copyright (c) 2009 Paul Carduner and Stephan Richter.
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
"""Setup"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    text = unicode(text, 'utf-8').encode('ascii', 'xmlcharrefreplace')
    return xml.sax.saxutils.escape(text)

setup (
    name = 'z3c.feature.core',
    version = '0.1.0',
    author = u"Paul Carduner and Stephan Richter",
    author_email = u"zope-dev@zope.org",
    description = u"Core Features to use with z3c.builder.core",
    long_description=(
        read('README.txt')
        +"\n\n"+
        read('CHANGES.txt')
        ),
    license = "ZPL",
    keywords = u"zope3 project builder feature",
    url = "http://pypi.python.org/pypi/z3c.feature.core",
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c','z3c.feature'],
    extras_require = {
        'test':[
            'zope.testing',
            'z3c.coverage',
            ],
        },
    install_requires = [
        'setuptools',
        'z3c.builder.core',
        ],
    zip_safe = False,
    entry_points = """
    [z3c.boiler.template]
    command-line = z3c.feature.core.template:CommandLineProjectTemplate
    python-package = z3c.feature.core.template:PythonPackageProjectTemplate

    [z3c.feature]
    meta-data = z3c.feature.core.metadata:MetaDataFeature
    comment-header-ZPL = z3c.feature.core.metadata:CommentHeaderZPLFeature
    proprietary-header = z3c.feature.core.metadata:ProprietaryHeaderFeature
    python-interpreter = z3c.feature.core.python:PythonInterpreterFeature
    script = z3c.feature.core.python:ScriptFeature
    unit-testing = z3c.feature.core.unittest:TestingFeature
    documentation = z3c.feature.core.metadata:DocumentationFeature

    [z3c.builderweb]
    meta-data = z3c.feature.core.web.metadata:MetaDataWebFeature
    comment-header-ZPL = z3c.feature.core.web.metadata:CommentHeaderZPLWebFeature
    proprietary-header = z3c.feature.core.web.metadata:ProprietaryHeaderWebFeature
    python-interpreter = z3c.feature.core.web.python:PythonInterpreterWebFeature
    script = z3c.feature.core.web.python:ScriptWebFeature
    unit-testing = z3c.feature.core.web.unittest:TestingWebFeature
    documentation = z3c.feature.core.web.metadata:DocumentationWebFeature
    """,
    )
