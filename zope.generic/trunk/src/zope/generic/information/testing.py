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

import zope.generic.testing.testing

from zope.app.testing import setup

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

        # register the directive of this package
        import zope.generic.information
        XMLConfig('meta.zcml', zope.generic.information)()        

    def tearDown(self, doctesttest=None):
        super(PlacelessSetup, self).tearDown(doctesttest)



placelesssetup = PlacelessSetup()
