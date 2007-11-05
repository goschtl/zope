##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Deprecared utility package

$Id$
"""

import sys
import warnings

warnings.warn("This module is deprecated and will go away in Zope 3.5. ",
              DeprecationWarning, 2)


import zope.deferredimport

zope.deferredimport.deprecated(
    "This object is deprecated and will go away in Zope 3.5",
    UtilityRegistration = "zope.app.component.back35:UtilityRegistration",
    )
