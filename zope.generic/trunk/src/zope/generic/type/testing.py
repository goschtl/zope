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

from zope.configuration.xmlconfig import XMLConfig

import zope.generic.configuration.testing

################################################################################
#
# Public Test implementations
#
################################################################################

def testInitializer(context, *pos, **kws):
    print context, pos, kws



################################################################################
#
# Placeless setup
#
################################################################################
    
# helper for directive testing
class PlacelessSetup(zope.generic.configuration.testing.PlacelessSetup):

    def setUp(self, doctesttest=None):
        super(PlacelessSetup, self).setUp(doctesttest)
        # register the directive of this package
        import zope.generic.type
        XMLConfig('meta.zcml', zope.generic.type)()

    def tearDown(self, doctesttest=None):
        super(PlacelessSetup, self).tearDown(doctesttest)



placelesssetup = PlacelessSetup()
