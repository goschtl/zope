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
"""Distribution class which ensure we can operate with or without Python 2.4.

$Id$
"""
import distutils.dist
import sys


if sys.version_info < (2, 3):
    distutils.dist.DistributionMetadata.classifiers = None
    distutils.dist.DistributionMetadata.download_url = None


class ZPkgDistribution(distutils.dist.Distribution):

    def __init__ (self, attrs=None):
        self.package_data = None
        distutils.dist.Distribution.__init__(self, attrs)
        if self.package_data and sys.version_info < (2, 4):
            from zpkgsetup.build_py import build_py
            self.cmdclass.setdefault('build_py', build_py)
