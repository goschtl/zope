##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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
    name = 'lovely.responsecache',
    version = '1.4.1',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    description = "Cache results of ContentProviders",
    license = "ZPL 2.1",
    keywords = "responsecache zope zope3",
    url = 'http://svn.zope.org/lovely.responsecache',
    zip_safe = False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely',],
    install_requires = ['setuptools',
                        'lovely.memcached',
                        'zope.app.publication',
                        'zope.app.security',
                        'zope.contentprovider',
                        'zope.formlib',
                        'zope.publisher',
                        'zope.schema',
                        'zope.security',
                        'zope.traversing'],
    extras_require = dict(
    pycurl = ['pycurl',],
    test = ['z3c.configurator',
            'z3c.testing',
            'zope.testbrowser',
            'zope.viewlet',
            'zope.pagetemplate',
            'zope.app.securitypolicy',
            'zope.app.zcmlfiles',
            'zope.app.testing',
            'zope.testing',]),
    )
