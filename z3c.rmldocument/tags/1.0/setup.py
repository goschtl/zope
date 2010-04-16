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
"""Setup
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='z3c.rmldocument',
    version = '1.0',
    author = "Christian Theune and the Zope Community",
    author_email = "zope3-dev@zope.org",
    description = "User-editable RML documents",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 rml reportlab pdf pagetemplate",
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent'],
    url = 'http://cheeseshop.python.org/pypi/z3c.rmldocument',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    install_requires = [
        'z3c.rml',
        'zope.app.pagetemplate',
        'setuptools',
        'lxml',
        ],
    include_package_data = True,
    zip_safe = False,
    )
