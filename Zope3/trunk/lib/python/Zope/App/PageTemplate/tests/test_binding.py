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

import unittest
from Zope.PageTemplate.tests import util
from Zope.App.PageTemplate.tests.testpackage.content \
     import Content, PTComponent

# Wow, this is a lot of work. :(
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.App.Traversing.Traverser import Traverser
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.App.Traversing.DefaultTraversable import DefaultTraversable
from Zope.App.Traversing.ITraversable import ITraversable
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter


class BindingTestCase(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(None, ITraverser, Traverser)
        provideAdapter(None, ITraversable, DefaultTraversable)

    def test_binding(self):
        comp = PTComponent(Content())
        self.assertEqual(comp.index(), "42\n")

def test_suite():
    return unittest.makeSuite(BindingTestCase)

if __name__=='__main__':
    unittest.main()
