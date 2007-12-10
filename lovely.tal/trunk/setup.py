##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
"""
$Id$
"""

__docformat__ = "reStructuredText"


from setuptools import setup, find_packages

setup(
    name = 'lovely.tal',
    version = '0.2.1',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    license = "ZPL. see LICENSE.txt",
    keywords = "tal zope zope3",
    url = 'svn://svn.zope.org/repos/main/lovely.tal',
    zip_safe = False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely',],
    install_requires = ['setuptools',
                        'zope.tales',
                        ],
    extras_require = dict(
        test = ['zope.app.testing',
                'zope.testing',]),
    )

