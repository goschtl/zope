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
from zope.component import provideAdapter
from zope.configuration.xmlconfig import XMLConfig
from zope.interface import Interface
from zope.schema import TextLine

import zope.generic.configuration.testing
import zope.generic.keyface.testing
import zope.generic.directlyprovides.testing
import zope.generic.testing.testing

################################################################################
#
# Public Test implementations
#
################################################################################

class IMarker(Interface):
    """Demo marker."""


class IBarConfiguration(Interface):

    bar = TextLine(title=u'Bar')


class IInputConfiguration(Interface):

    foo = TextLine(title=u'Foo')

    bar = TextLine(title=u'Bar')


class IFooConfiguration(Interface):

    foo = TextLine(title=u'Foo')
    
    fo = TextLine(title=u'Fo', required=False, readonly=True, default=u'fo default')


class TestKeyfaceAttriute(object):
    __keyface__ = IFooConfiguration


################################################################################
#
# Placeless setup
#
################################################################################

# specific tests
def setUp(doctest=None):
    # register attribute configurations adapter
    import zope.generic.configuration.adapter
    from zope.generic.configuration import IConfigurations
    provideAdapter(zope.generic.configuration.adapter.AttributeConfigurations,
        provides=IConfigurations)

    # register the directive of this package
    import zope.generic.configuration
    XMLConfig('meta.zcml', zope.generic.configuration)()

def tearDown(doctest=None):
    pass



class PlacelessSetup(zope.app.testing.placelesssetup.PlacelessSetup):

    def setUp(self, doctest=None):
        super(PlacelessSetup, self).setUp(doctest)
        # external setup
        zope.generic.testing.testing.setUp(doctest)
        zope.generic.directlyprovides.testing.setUp(doctest)
        zope.generic.keyface.testing.setUp(doctest)
        zope.generic.configuration.testing.setUp(doctest)
        # internal setup
        setUp(doctest)

    def tearDown(self, doctest=None):
        super(PlacelessSetup, self).tearDown()
        # external teardown
        zope.generic.configuration.testing.tearDown(doctest)
        zope.generic.keyface.testing.tearDown(doctest)
        zope.generic.directlyprovides.testing.tearDown(doctest)
        zope.generic.testing.testing.tearDown(doctest)
        # internal teardown
        tearDown(doctest)

placelesssetup = PlacelessSetup()
