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
import zope.generic.adapter.testing
import zope.generic.configuration.testing
import zope.generic.directlyprovides.testing
import zope.generic.factory.testing
import zope.generic.handler.testing
import zope.generic.face.testing
import zope.generic.operation.testing
import zope.generic.testing.testing

from zope.configuration.xmlconfig import XMLConfig



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

# specific tests
def setUp(doctest=None):
    # register the directive of this package
    import zope.generic.content
    XMLConfig('meta.zcml', zope.generic.content)()

def tearDown(doctest=None):
    pass



class PlacelessSetup(zope.app.testing.placelesssetup.PlacelessSetup):

    def setUp(self, doctest=None):
        super(PlacelessSetup, self).setUp(doctest)
        # external setup
        zope.generic.testing.testing.setUp(doctest)
        zope.generic.directlyprovides.testing.setUp(doctest)
        zope.generic.face.testing.setUp(doctest)
        zope.generic.configuration.testing.setUp(doctest)
        zope.generic.operation.testing.setUp(doctest)
        zope.generic.factory.testing.setUp(doctest)
        zope.generic.adapter.testing.setUp(doctest)
        zope.generic.handler.testing.setUp(doctest)
        # internal setup
        setUp(doctest)

    def tearDown(self, doctest=None):
        # internal teardown
        tearDown(doctest)
        # external teardown
        zope.generic.handler.testing.tearDown(doctest)
        zope.generic.adapter.testing.tearDown(doctest)
        zope.generic.factory.testing.tearDown(doctest)
        zope.generic.operation.testing.tearDown(doctest)
        zope.generic.configuration.testing.tearDown(doctest)
        zope.generic.face.testing.tearDown(doctest)
        zope.generic.directlyprovides.testing.tearDown(doctest)
        zope.generic.testing.testing.tearDown(doctest)
        super(PlacelessSetup, self).tearDown()

placelesssetup = PlacelessSetup()
