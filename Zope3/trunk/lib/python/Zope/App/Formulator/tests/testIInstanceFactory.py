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
"""
This suite will test whether the IInstanceFactory will work correctly. In
order to save some dependencies, we will implement a stub for the test.

$Id: testIInstanceFactory.py,v 1.2 2002/06/10 23:27:50 jim Exp $
"""

import unittest
from Zope.App.Formulator.IInstanceFactory import IInstanceFactory


class ContentObject:
    """Content Object stub that will provide the context fir the
       InstanceFactory"""
    pass


class Factory:
    """InstanceFactory stub."""

    __implements__ = IInstanceFactory


    context = None

    ############################################################
    # Implementation methods for interface
    # Zope.App.Formulator.IInstanceFactory.

    def __call__(self, context):
        '''See interface IInstanceFactory'''
        self.realize(context)

    def realize(self, context):
        '''See interface IInstanceFactory'''
        self.context = context
    #
    ############################################################



class Test(unittest.TestCase):


    def testRealize(self):
        context = ContentObject()
        factory = Factory()
        factory.realize(context)
        self.assertEqual(factory.context, context)


    def testCall(self):
        context = ContentObject()
        factory = Factory()
        factory(context)
        self.assertEqual(factory.context, context)


    def testGetContext(self):
        context = ContentObject()
        factory = Factory()
        factory.context = context
        self.assertEqual(factory.context, context)

        

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)


if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
