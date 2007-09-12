##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Ape -- Adaptable Persistence Engine.

$Id$
"""

import os
import sys

# Import the copy of apelib from 'lib' by temporarily changing sys.path.
old_path = sys.path[:]
here = __path__[0]
sys.path.insert(0, os.path.join(here, 'lib'))
try:
    import apelib
finally:
    # Restore sys.path
    sys.path[:] = old_path

from apelib.zope2.setup import patches
patches.apply_patches()
