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
"""Unit test logic for setting up and tearing down basic infrastructure


$Id: PlacelessSetup.py,v 1.3 2002/11/19 23:25:15 jim Exp $
"""

from Zope.ComponentArchitecture.tests.PlacelessSetup \
     import PlacelessSetup as CAPlacelessSetup
from Zope.App.ComponentArchitecture.tests.PlacelessSetup \
     import PlacelessSetup as ACAPlacelessSetup
from Zope.Event.tests.PlacelessSetup \
     import PlacelessSetup as EventPlacelessSetup


class PlacelessSetup(CAPlacelessSetup, ACAPlacelessSetup, EventPlacelessSetup):

    def setUp(self):
        CAPlacelessSetup.setUp(self)
        ACAPlacelessSetup.setUp(self)
        EventPlacelessSetup.setUp(self)
