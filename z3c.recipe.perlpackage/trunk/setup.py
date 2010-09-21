##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = "z3c.recipe.perlpackage"
version = '0.1'

setup(
    name = name,
    version = version,
    author = "Kevin Teague",
    author_email = "kevin@bud.ca",
    description = "ZC Buildout recipe for installing a Perl package",
    license = "ZPL 2.1",
    keywords = "buildout",
    url='http://www.python.org/pypi/'+name,
    long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        ),

    packages = find_packages(),
    include_package_data = True,
    data_files = [('.', ['README.txt'])],
    namespace_packages = ['z3c', 'z3c.recipe'],
    install_requires = ['zc.buildout', 'setuptools'],
    entry_points = {'zc.buildout':
                    ['default = %s:Recipe' % name]},
    zip_safe = True,
    )
