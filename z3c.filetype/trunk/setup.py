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
"""Setup for z3c.filetype package

$Id: setup.py 82381 2007-12-21 10:08:32Z jukart $
"""

import os.path
from setuptools import setup, find_packages

def read(*path_elements):
    return "\n\n" + file(os.path.join(*path_elements)).read()

setup(
    name="z3c.filetype",
    version="1.2.1",
    namespace_packages=["z3c"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    license='ZPL 2.1',
    description="Get interfaces for objects based on their content, "\
                "filename or mime-type.",
    long_description=(
        '.. contents::' +
        read('src', 'z3c', 'filetype', 'README.txt') +
        read('src', 'z3c', 'filetype', 'magic.txt') +
        read('src', 'z3c', 'filetype', 'TODO.txt') +
        read('CHANGES.txt')
        ),
    install_requires=[
        "setuptools",
        "zope.cachedescriptors",
        "zope.component",
        "zope.contenttype",
        "zope.event",
        "zope.i18nmessageid",
        "zope.interface",
        "zope.lifecycleevent",
        "zope.proxy",
        "zope.schema",
        "zope.size",
        ],
    extras_require={
        "test": ["zope.testing"],
        },
    zip_safe=False,
    )
