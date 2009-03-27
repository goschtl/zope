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
    name = 'z3c.feature.zope',
    version = '0.1.0',
    author = u"Paul Carduner and Stephan Richter",
    author_email = u"zope-dev@zope.org",
    description = u"Zope Features to use with z3c.builder.core",
    long_description=(
        read('README.txt')
        +"\n\n"+
        read('CHANGES.txt')
        ),
    license = "ZPL",
    keywords = u"zope3 project builder feature",
    url = "http://pypi.python.org/pypi/z3c.feature.zope",
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
        'z3c.feature.core',
        ],
    zip_safe = False,
    entry_points = """
    [z3c.boiler.template]
    zope-project = z3c.feature.zope.template:ZopeProjectTemplate

    [z3c.feature]
    zope-project = z3c.feature.zope.project:ZopeProjectFeature
    zope-page = z3c.feature.zope.browser:ZopePageFeature
    zope-skin = z3c.feature.zope.skin:ZopeSkinFeature
    content-type = z3c.feature.zope.content:ZopeContentFeature

    [z3c.builderweb]
    zope-page = z3c.feature.zope.web.page:ZopePageWebFeature
    zope-project = z3c.feature.zope.web.project:ZopeProjectWebFeature
    content-type = z3c.feature.zope.web.content:ZopeContentWebFeature
    """,
    )
