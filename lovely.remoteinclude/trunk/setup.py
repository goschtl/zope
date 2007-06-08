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
    name = 'lovely.remoteinclude',
    version = '0.2.2',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    license = "ZPL 2.1",
    keywords = "remoteinclude includes zope zope3",
    description = "render include views of viewlets and views",
    url = 'http://svn.zope.org/lovely.remoteinclude',
    zip_safe = False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely',],
    extras_require = dict(
        test = ['zope.app.testing',
                'zope.app.zcmlfiles',
                'zope.app.securitypolicy',
                'zope.testbrowser',
                'zope.app.server',
                'zope.contentprovider',
                'zope.viewlet',
                'z3c.traverser >= 0.1.3',
                'z3c.configurator',
                'zc.selenium',
                'z3c.testing']
        ),
    install_requires = ['zope.component',
                        'lovely.responsecache >= 0.2.1',
                        'zope.cachedescriptors',
                        'zope.contentprovider',
                        'zope.publisher',
                        'zope.traversing',
                        ],
    )
