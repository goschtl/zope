##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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

import os.path

from setuptools import setup, find_packages


setup(
    name = 'gocept.registration',
    version = "0.1",
    author = "Christian Theune, Stephan Richter and others",
    author_email = "mail@gocept.com",
    description = "User self-registration",
    long_description = file(os.path.join(os.path.dirname(__file__),
                                         'src', 'gocept', 'registration',
                                         'README.txt')).read(),
    license = "ZPL 2.1",
    url='http://pypi.python.org/pypi/gocept.registration/',

    packages = find_packages('src'),
    package_dir = {'': 'src'},

    include_package_data = True,
    zip_safe = False,

    namespace_packages = ['gocept'],
    install_requires = [
        'setuptools',
        'zope.app.container',
        'zope.component',
        'zope.interface',
        'zope.sendmail',
        'z3c.form'
    ],
    extras_require = dict(
        test=['zope.testing',
              'zope.app.twisted',
              'zope.app.securitypolicy',
              'z3c.formui',
              'z3c.layer'])
    )
