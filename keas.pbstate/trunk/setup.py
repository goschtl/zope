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
"""An object database foundation based on Google's Protocol Buffers"""

import os
from setuptools import setup

VERSION='0.2dev'

def read_file(*path):
    base_dir = os.path.dirname(__file__)
    file_path = (base_dir, ) + tuple(path)
    return file(os.path.join(*file_path)).read()

setup(
    name='keas.pbstate',
    version=VERSION,
    author='Shane Hathaway and the Zope Community',
    author_email='zope-dev@zope.org',
    description=__doc__,
    license='ZPL 2.1',

    package_dir={'': 'src'},
    packages=['keas', 'keas.pbstate'],
    namespace_packages=['keas'],
    install_requires=[
        'setuptools',
        'protobuf',
        ],
    long_description = read_file('src', 'keas', 'pbstate', 'README.txt'),
)
