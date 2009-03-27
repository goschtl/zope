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
from setuptools import setup, find_packages

setup (
    name = 'z3c.boilerweb',
    version = '0.1.0',
    author = u"Paul Carduner and Stephan Richter",
    author_email = u"zope-dev@zope.org",
    description = u"A Web Front End to the z3c.boiler",
    license = "ZPL",
    keywords = u"zope3 project builder",
    url = "http://pypi.python.org/pypi/z3c.boilerweb",
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = [],
    extras_require = {
        'test':[
            'zope.testing',
            'z3c.coverage',
            'zc.selenium'
            ],
    },
    install_requires = [
        'ZConfig',
        'ZODB3',
        'docutils',
        'setuptools',
        'z3c.builder.core',
        'z3c.feature.core',
        'z3c.form',
        'z3c.formui',
        'z3c.layer.pagelet',
        'z3c.macro',
        'z3c.menu.ready2go',
        'z3c.pagelet',
        'z3c.template',
        'z3c.versionedresource',
        'zc.configuration',
        'zdaemon',
        'zope.app.appsetup',
        'zope.app.authentication',
        'zope.app.securitypolicy',
        'zope.app.twisted',
        'zope.app.wsgi',
        'zope.app.zcmlfiles',
        'zope.publisher',
        'zope.session',
        'zope.traversing',
        ],
    zip_safe = False,
    )
