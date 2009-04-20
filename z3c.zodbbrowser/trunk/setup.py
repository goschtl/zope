##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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

from setuptools import setup, find_packages

setup(
    name="z3c.zodbbrowser",
    version="0.1",
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    description='ZODB Browser',

    packages=find_packages('src'),
    package_dir={"": "src"},
    namespace_packages=['z3c'],

    install_requires=["setuptools",
                      "ZODB3",
                      ],
    entry_points={'console_scripts':
                      ['zodbbrowser = z3c.zodbbrowser.main:main']},
    include_package_data=True,
    zip_safe=False,
    )
