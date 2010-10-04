##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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

import zope.interface

from zope.container.tests.test_icontainer import DefaultTestData
from zope.container import contained

from z3c.resource import interfaces
from z3c import testing


################################################################################
#
# Resource Test implementations
#
################################################################################

class Content(object):
    """Test content."""

    zope.interface.implements(interfaces.IResourceTraversable)



class TestResourceItem(contained.Contained, object):
    """Test resource item."""

    zope.interface.implements(interfaces.IResourceItem)


################################################################################
#
# Resource Base Tests
#
################################################################################

class BaseTestIResource(testing.BaseTestIContainer):

    def getTestInterface(self):
        return interfaces.IResource

    def makeTestData(self):
        return DefaultTestData()

    def getUnknownKey(self):
        return '10'

    def getBadKeyTypes(self):
        return [None, ['foo'], 1, '\xf3abc']


class BaseTestIResourceItem(testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IResourceItem
