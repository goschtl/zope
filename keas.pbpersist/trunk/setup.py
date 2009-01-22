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

from setuptools import setup

setup(
    name='keas.pbpersist',
    version='0.1dev',
    author='Shane Hathaway and the Zope Community',
    author_email='zope-dev@zope.org',
    description='ZODB Persistence in a Google Protocol Buffer',
    license='ZPL 2.1',

    package_dir={'': 'src'},
    packages=['keas.pbpersist'],
    namespace_packages=['keas'],
    install_requires=[
        'setuptools',
        'keas.pbstate',
        'ZODB3',
        ],
)
