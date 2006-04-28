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

import zope.app.testing.placelesssetup
import zope.generic.testing.testing

from zope.component import provideHandler



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

# specific tests
def setUp(doctest=None):
    # handlers
    from zope.generic.directlyprovides.handler import notifyObjectModifiedEvent
    from zope.generic.directlyprovides import IDirectlyProvidesModifiedEvent
    provideHandler(notifyObjectModifiedEvent, [IDirectlyProvidesModifiedEvent])

def tearDown(doctest=None):
    pass



class PlacelessSetup(zope.app.testing.placelesssetup.PlacelessSetup):

    def setUp(self, doctest=None):
        super(PlacelessSetup, self).setUp(doctest)
        # external setup
        zope.generic.testing.testing.setUp(doctest)
        # internal setup
        setUp(doctest)

    def tearDown(self, doctest=None):
        super(PlacelessSetup, self).tearDown()
        # external teardown
        zope.generic.testing.testing.tearDown(doctest)
        # internal teardown
        tearDown(doctest)

placelesssetup = PlacelessSetup()
