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
"""ZODB Persistence in a Google Protocol Buffer"""

import os
from setuptools import setup

VERSION = '0.1'

def read_file(*path):
    base_dir = os.path.dirname(__file__)
    file_path = (base_dir, ) + tuple(path)
    return file(os.path.join(*file_path)).read()

setup(
    name='keas.pbpersist',
    version=VERSION,
    author='Shane Hathaway and the Zope Community',
    author_email='zope-dev@zope.org',
    description=__doc__,
    license='ZPL 2.1',

    package_dir={'': 'src'},
    packages=['keas', 'keas.pbpersist'],
    namespace_packages=['keas'],
    install_requires=[
        'setuptools',
        'keas.pbstate',
        'ZODB3',
        ],
    long_description = read_file('src', 'keas', 'pbpersist', 'README.txt'),
)
