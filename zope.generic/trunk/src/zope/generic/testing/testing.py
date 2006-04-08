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


from cStringIO import StringIO
from zope.configuration.xmlconfig import XMLConfig
from zope.configuration.xmlconfig import xmlconfig
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject
import unittest

from zope.component import provideAdapter
import zope.app.testing.placelesssetup


################################################################################
#
# Base Test implementations
#
################################################################################



_marker_pos = object()
_marker_kws = object()

class InterfaceBaseTest(unittest.TestCase):
    """Base class for interface based unit tests."""

    _test_interface = None
    _test_class = None
    _test_pos = None
    _test_kws = None
    _verify_class = True
    _verify_object = True

    def makeTestObject(self, *pos, **kws):
        # assert defaults for positional or keyword arguments
        if not pos and self._test_pos is not None:
            pos = self._test_pos

        if not kws and self._test_kws is not None:
            kws = self._test_kws
       
        return self._test_class(*pos, **kws)

    def test_verify_class(self):
        if self._verify_class:
            self.assert_(verifyClass(self._test_interface, self._verify_class)) 

    def test_verify_object(self):
        if self._verify_object:
            self.assert_(verifyObject(self._test_interface, self.makeTestObject()))



################################################################################
#
# Placeless setup
#
################################################################################
    
# helper for directive testing
template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:generic='http://namespaces.zope.org/generic'
   xmlns:test='http://www.zope.org/NS/Zope3/test'
   i18n_domain='zope'>
   %s
   </configure>"""


def registerDirective(direcitive):
        xmlconfig(StringIO(template % direcitive))



class PlacelessSetup(zope.app.testing.placelesssetup.PlacelessSetup):

    def setUp(self, doctesttest=None):
        super(PlacelessSetup, self).setUp(doctesttest)

        # zope.app.annotations
        from zope.app.annotation.interfaces import IAnnotations
        from zope.app.annotation.interfaces import IAttributeAnnotatable
        from zope.app.annotation.attribute import AttributeAnnotations

        provideAdapter(AttributeAnnotations, adapts=[IAttributeAnnotatable], 
                       provides=IAnnotations)

        # zcml configurations
        import zope.app.component
        XMLConfig('meta.zcml', zope.app.component)()
        import zope.app.security
        XMLConfig('meta.zcml', zope.app.security)()

    def tearDown(self, doctesttest=None):
        super(PlacelessSetup, self).tearDown()



placelesssetup = PlacelessSetup()
