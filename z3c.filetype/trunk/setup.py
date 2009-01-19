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
"""Setup for z3c.filetype package

$Id: setup.py 82381 2007-12-21 10:08:32Z jukart $
"""

from setuptools import setup, find_packages

setup(
    name="z3c.filetype",
    version="1.2.0",
    namespace_packages=["z3c"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
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
