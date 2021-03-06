##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Setup for zope.app.applicationcontrol package

$Id$
"""

import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.applicationcontrol',
    version = '3.5.0',
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    description='Zope applicationcontrol',
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('INSTALL.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license='ZPL 2.1',
    keywords = "zope3 application control",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url='http://cheeseshop.python.org/pypi/zope.app.applicationcontrol',
    extras_require=dict(
        test=['zope.app.testing']),
    package_dir = {'': 'src'},
    packages=find_packages('src'),
    namespace_packages=['zope', 'zope.app'],
    install_requires=[
        'setuptools',
        'zope.error',
        'zope.interface',
        'zope.i18n',
        'zope.size',
        'zope.traversing>=3.7.0',
        ],
    include_package_data = True,
    zip_safe = False,
    )
