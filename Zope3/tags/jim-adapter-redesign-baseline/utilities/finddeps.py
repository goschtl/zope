#!/usr/bin/env python2.3
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
"""Script to search for package dependencies.

$Id$
"""

import os
import sys

here = os.path.dirname(os.path.realpath(__file__))
swhome = os.path.dirname(here)

for parts in [("src",), ("lib", "python"), ("Lib", "site-packages")]:
    d = os.path.join(swhome, *(parts + ("zope", "app", "appsetup")))
    if os.path.isdir(d):
        d = os.path.join(swhome, *parts)
        sys.path.insert(0, d)
        break
else:
    print >>sys.stderr, "Could not locate Zope software installation!"
    sys.exit(1)


from zope.dependencytool.finddeps import main


main()
