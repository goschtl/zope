##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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
name = 'zc.zopeorgkeyupload'
version = '0.1'

from setuptools import setup, find_packages

entry_points = """
[zope.publisher.publication_factory]
default = zc.zopeorgkeyupload:Publication

[console_scripts]
mvkey = zc.zopeorgkeyupload.mvkey:main
"""

setup(
    name = name,
    version = version,
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = '',
    license = 'ZPL 2.1',
    
    packages = find_packages('src'),
    namespace_packages = ['zc'],
    package_dir = {'': 'src'},
    install_requires = ['setuptools',
                        'zope.security',
                        'zope.app.security',
                        ],
    zip_safe = False,
    entry_points=entry_points,
    include_package_data = True,
    )
