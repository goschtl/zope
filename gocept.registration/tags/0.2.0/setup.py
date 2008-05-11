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

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name = 'gocept.registration',
    version = "0.2.0",
    author = "Christian Theune, Stephan Richter and others",
    author_email = "mail@gocept.com",
    description = "User self-registration",
    long_description = (read('README.txt')
                        + '\n\n' +
                        read('src', 'gocept', 'registration',
                            'README.txt')
                        + '\n\n' +
                        read('CHANGES.txt')
    ),
    license = "ZPL 2.1",
    url='http://pypi.python.org/pypi/gocept.registration/',
    keywords = "zope3 gocept user registration",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],


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
              'zope.testbrowser',
              'z3c.formui',
              'z3c.layer'])
    )
