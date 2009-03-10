##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Setup for z3c.ownership package

$Id$
"""
import os
from setuptools import find_packages, setup

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='z3c.ownership',
    version='0.1.0dev',
    author='Dan Korostelev and Zope Community',
    author_email='zope-dev@zope.org',
    description='Object ownership functionality based on zope.securitypolicy',
    long_description=(
        read('README.txt')
        + '\n.. contents::\n\n' +
        read('src', 'z3c', 'ownership', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    keywords="zope security ownership",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'
        ],
    url='http://pypi.python.org/pypi/z3c.ownership',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    install_requires=[
        'setuptools',
        'zope.app.security',
        'zope.component',
        'zope.event',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.proxy',
        'zope.schema',
        'zope.security',
        'zope.securitypolicy',
        ],
    include_package_data=True,
    zip_safe=False,
    )
