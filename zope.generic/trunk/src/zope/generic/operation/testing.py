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

import zope.app.testing.placelesssetup
import zope.generic.component.testing
import zope.generic.configuration.testing
import zope.generic.directlyprovides.testing
import zope.generic.information.testing
import zope.generic.operation
import zope.generic.testing.testing

from zope.generic.information.api import provideInformation
from zope.generic.operation import IOperationInformation



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
    # register operation information registry
    provideInformation(IOperationInformation)

    # register the directive of this package
    XMLConfig('meta.zcml', zope.generic.operation)()

def tearDown(doctest=None):
    pass



class PlacelessSetup(zope.app.testing.placelesssetup.PlacelessSetup):

    def setUp(self, doctest=None):
        super(PlacelessSetup, self).setUp(doctest)
        # external setup
        zope.generic.testing.testing.setUp(doctest)
        zope.generic.directlyprovides.testing.setUp(doctest)
        zope.generic.component.testing.setUp(doctest)
        zope.generic.information.testing.setUp(doctest)
        zope.generic.configuration.testing.setUp(doctest)
        # internal setup
        setUp(doctest)

    def tearDown(self, doctest=None):
        super(PlacelessSetup, self).tearDown()
        # external teardown
        zope.generic.testing.testing.tearDown(doctest)
        zope.generic.directlyprovides.testing.tearDown(doctest)
        zope.generic.component.testing.tearDown(doctest)
        zope.generic.information.testing.tearDown(doctest)
        zope.generic.configuration.testing.tearDown(doctest)
        # internal teardown
        tearDown(doctest)

placelesssetup = PlacelessSetup()
