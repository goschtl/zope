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

from zope.component import provideAdapter
from zope.configuration.xmlconfig import XMLConfig
from zope.interface import Interface
from zope.schema import TextLine

from zope.generic.configuration import IConfigurations

import zope.generic.information.testing


################################################################################
#
# Public Test implementations
#
################################################################################

class IMarker(Interface):
    """Demo marker."""


class IFooConfiguration(Interface):

    foo = TextLine(title=u'Foo')
    
    fo = TextLine(title=u'Fo', required=False, readonly=True, default=u'fo default')


class IBarConfiguration(Interface):

    bar = TextLine(title=u'Bar')


class IInputConfiguration(Interface):

    foo = TextLine(title=u'Foo')

    bar = TextLine(title=u'Bar')



################################################################################
#
# Placeless setup
#
################################################################################


class PlacelessSetup(zope.generic.information.testing.PlacelessSetup):

    def setUp(self, doctesttest=None):
        super(PlacelessSetup, self).setUp(doctesttest)

        # register attribute configurations adapter
        import zope.generic.configuration.adapter
        provideAdapter(zope.generic.configuration.adapter.AttributeConfigurations,
            provides=IConfigurations)

        # register the directive of this package
        import zope.generic.configuration
        XMLConfig('meta.zcml', zope.generic.configuration)()

    def tearDown(self, doctesttest=None):
        super(PlacelessSetup, self).tearDown(doctesttest)



placelesssetup = PlacelessSetup()
