##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests to check talesapi zcml configuration

$Id: test_directives.py,v 1.1 2003/04/15 18:52:58 matth Exp $
"""

import unittest
from cStringIO import StringIO

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.configuration.exceptions import ConfigurationError
from zope.app.security.exceptions import UndefinedPermissionError

from zope.app.tests.placelesssetup import PlacelessSetup

from zope.interface import Interface
from zope.component.adapter import provideAdapter
from zope.app.interfaces.traversing import ITraversable

template = """<zopeConfigure 
   xmlns='http://namespaces.zope.org/zope'
   xmlns:tales='http://namespaces.zope.org/tales'>
   %s
   </zopeConfigure>"""


def definePermissions():
    XMLConfig('meta.zcml', zope.app.pagetemplate)()


class I(Interface):
    pass

class Adapter:
    __implements__ = (I, ITraversable)

    def __init__(self, context):
        pass
  
    def title(self):
        return "42" 

    def traverse(self, name, *args):
        return getattr(self, name)

class Test(PlacelessSetup, unittest.TestCase):

    # XXX: tests for other directives needed

    def setUp(self):
        import zope.configuration
        PlacelessSetup.setUp(self)
        XMLConfig('metameta.zcml', zope.configuration)()
        XMLConfig('meta.zcml', zope.app.pagetemplate)()

    def testTalesAPI1(self):
        from zope.app.pagetemplate.engine import Engine

        provideAdapter(None, I, Adapter)

        xmlconfig(StringIO(template % (
            """
            <tales:namespace 
              prefix="zope"
              interface="zope.app.pagetemplate.tests.test_directives.I"
              />
            """
            )))


        e = Engine.compile('context/zope:title')
        res = e(Engine.getContext(context = None))

        self.assertEqual(res, '42')


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)
if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
