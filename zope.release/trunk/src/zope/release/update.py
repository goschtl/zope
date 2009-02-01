##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Update indexes of all versions.

Usage: update-index site-dir

* ``site-dir``

  The directory that contains the KGS Web site.
"""
import os
import sys
from zope.release.mirror import mirrorcheeseshopslashsimple as mirror

mirror.controlled_packages_path = os.path.join('..', 'controlled-packages.cfg')

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) != 1:
        print __doc__
        sys.exit(1)

    siteDir = args[-1]

    for filename in os.listdir(siteDir):
        path = os.path.join(siteDir, filename)
        if os.path.isdir(path) and 'index' in os.listdir(path):
            mirror.update([os.path.join(path, 'index')])
