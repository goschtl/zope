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


$Id: placelesssetup.py,v 1.3 2003/03/25 20:42:53 jim Exp $
"""

from zope.component.tests.placelesssetup \
     import PlacelessSetup as CAPlacelessSetup
from zope.app.component.tests.placelesssetup \
     import PlacelessSetup as ACAPlacelessSetup
from zope.app.event.tests.placelesssetup \
     import PlacelessSetup as EventPlacelessSetup
from zope.app.i18n.tests.placelesssetup \
     import PlacelessSetup as I18nPlacelessSetup


class PlacelessSetup(CAPlacelessSetup,
                     ACAPlacelessSetup,
                     EventPlacelessSetup,
                     I18nPlacelessSetup,
                     ):

    def setUp(self):
        CAPlacelessSetup.setUp(self)
        ACAPlacelessSetup.setUp(self)
        EventPlacelessSetup.setUp(self)
        I18nPlacelessSetup.setUp(self)
