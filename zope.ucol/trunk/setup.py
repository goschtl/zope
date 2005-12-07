##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Setup for zope.ucol package

$Id$
"""

import sys
from distutils.core import setup, Extension

if sys.platform.startswith('win'):
    libraries = ['icuin', 'icuuc', 'icudt']
else:
    libraries=['icui18n', 'icuuc', 'icudata']

setup(name='zope.ucol',
      version='1.0',
      ext_modules=[
          Extension('zope.ucol._zope_ucol',
                    ['src/zope/ucol/_zope_ucol.c'],
                    libraries=libraries,
           )
          ],
      packages=["zope", "zope.ucol"],
      package_dir = {'': 'src'},
      )
