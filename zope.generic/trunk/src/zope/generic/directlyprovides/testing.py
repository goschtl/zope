##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""
$Id$
"""

__docformat__ = 'restructuredtext'

from zope.app.testing import ztapi
import zope.generic.testing.testing


################################################################################
#
# Public Test implementations
#
################################################################################



################################################################################
#
# Placeless setup
#
################################################################################



class PlacelessSetup(zope.generic.testing.testing.PlacelessSetup):

    def setUp(self, doctesttest=None):
        super(PlacelessSetup, self).setUp(doctesttest)

        # handlers
        from zope.generic.directlyprovides.handler import notifyObjectModifiedEvent
        from zope.generic.directlyprovides import IDirectlyProvidesModifiedEvent
        ztapi.subscribe([IDirectlyProvidesModifiedEvent], 
            None, notifyObjectModifiedEvent)
        
    def tearDown(self, doctesttest=None):
        super(PlacelessSetup, self).tearDown()



placelesssetup = PlacelessSetup()
