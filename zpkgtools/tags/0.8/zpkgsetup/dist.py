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
"""Distribution class which ensures we can operate with or without Python 2.4.

$Id$
"""
import distutils.dist
import distutils.extension
import sys


class ZPkgExtension(distutils.extension.Extension):
    """Distutils representation of a compiled extension module."""


class ZPkgDistribution(distutils.dist.Distribution):
    """Distribution that ensures features needed by **zpkg** are available."""

    def __init__ (self, attrs=None):
        self.package_data = None
        distutils.dist.Distribution.__init__(self, attrs)
        if self.package_data and sys.version_info < (2, 4):
            from zpkgsetup.build_py import build_py
            from zpkgsetup.install_lib import install_lib
            self.cmdclass.setdefault('build_py', build_py)
            self.cmdclass.setdefault('install_lib', install_lib)
