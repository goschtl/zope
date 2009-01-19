#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Setup for z3c.recipe.sphinxdoc package

$Id$
"""

# Check python version
import sys
if sys.version_info < (2, 4):
    print >> sys.stderr, '%s: need Python 2.4 or later.' % sys.argv[0]
    print >> sys.stderr, 'Your python is %s' % sys.version
    sys.exit(1)

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="z3c.recipe.sphinxdoc",
    version='0.0.6dev',
    author="Paul Carduner",
    description="Use Sphinx to build documentation for zope.org.",
    long_description=(read(os.path.join('src','z3c','recipe','sphinxdoc','index.txt'))
                      +'\n\n'+
                      read('CHANGES.txt')),
    license="ZPL 2.1",
    maintainer="Paul Carduner",
    maintainer_email="zope-dev@zope.org",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"],
    url='http://pypi.python.org/pypi/z3c.recipe.sphinxdoc/',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c','z3c.recipe'],
    install_requires=['setuptools',
                      'zc.buildout',
                      'zc.recipe.egg',
                      'Sphinx'],
    entry_points="""
    [zc.buildout]
    default = z3c.recipe.sphinxdoc:ZopeOrgSetup
    """,
    zip_safe=False,
    include_package_data=True,
    )
