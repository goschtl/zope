##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Test the gts ZCML namespace directives.

$Id: test_helpdirectives.py,v 1.3 2003/07/15 14:20:15 srichter Exp $
"""
import os
import unittest

from cStringIO import StringIO

from zope.interface import Interface
from zope.component.adapter import provideAdapter
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.configuration.xmlconfig import xmlconfig, Context, XMLConfig
from zope.app.interfaces.traversing import \
     ITraverser, ITraversable, IPhysicallyLocatable
from zope.app.traversing.adapters import \
     Traverser, DefaultTraversable, WrapperPhysicallyLocatable

import zope.app.onlinehelp
from zope.app.onlinehelp import help
from zope.app.onlinehelp.tests.test_onlinehelptopic import testdir

template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:help='http://namespaces.zope.org/help'>
   xmlns:test='http://www.zope.org/NS/Zope3/test'>
   %s
   </zopeConfigure>"""

class I1(Interface):
    pass


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(None, ITraverser, Traverser)
        provideAdapter(None, ITraversable, DefaultTraversable)
        provideAdapter(None, IPhysicallyLocatable, WrapperPhysicallyLocatable)
        XMLConfig('meta.zcml', zope.app.onlinehelp)()

    def test_register(self):
        self.assertEqual(help.keys(), [])
        xmlconfig(StringIO(template % (
            '''
              <help:register 
                  id = "help1"
                  title = "Help"
                  for = "zope.app.onlinehelp.tests.test_helpdirectives.I1"
                  view = "view.html"
                  doc_path = "./help.txt" />
                  '''
            )), None, Context([], zope.i18n.tests))
        self.assertEqual(help.keys(), ['help1'])
        self.assertEqual(help._registry[(I1, 'view.html')][0].title, 'Help')
        help._register = {}
        del help['help1']

    def test_unregister(self):
        self.assertEqual(help.keys(), [])
        path = os.path.join(testdir(), 'help.txt')
        help.registerHelpTopic('', 'help', 'Help',
                               path, 'txt', I1, 'view.html')

        xmlconfig(StringIO(template % (
            '''
              <help:unregister path="help" />
              '''
            )), None, Context([], zope.i18n.tests))
        self.assertEqual(help.keys(), [])



def test_suite():
    return unittest.makeSuite(DirectivesTest)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
