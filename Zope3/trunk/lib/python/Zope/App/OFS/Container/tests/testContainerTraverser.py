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

$Id: testContainerTraverser.py,v 1.2 2002/06/10 23:27:57 jim Exp $
"""

import unittest, sys
from Zope.ComponentArchitecture.tests.Request import Request
from Zope.ComponentArchitecture import getService
from Zope.App.OFS.Container.ContainerTraverser import ContainerTraverser
from Interface import Interface
from Zope.Exceptions import NotFoundError
from Zope.App.OFS.Container.IContainer import IContainer
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup

class I(Interface): pass


class Container:

    __implements__ = IContainer

    def __init__(self, **kw):

        for k in kw:
            setattr(self, k , kw[k])


    def get(self, name, default=None):
        
        return getattr(self, name, default)

    

class Request(Request):

    def getEffectiveURL(self):
        return ''

class View:

    def __init__(self, comp, request):
        self._comp = comp



class Test(PlacelessSetup, unittest.TestCase):

    def testAttr(self):
        """ test container traver """

        foo = Container()
        c   = Container( foo=foo )
        req = Request( I, '')
        
        T = ContainerTraverser(c, req)
        self.failUnless(T.publishTraverse(req,'foo') is foo)
        
        self.assertRaises(NotFoundError , T.publishTraverse, req ,'morebar')


    def testView(self):
        """ test getting a view """
        

        foo = Container()
        c   = Container( foo=foo )
        req = Request( I, '')
        
        T = ContainerTraverser(c, req)
        getService(None,'Views').provideView(IContainer, 'viewfoo', I, [View])
        
        self.failUnless(T.publishTraverse(req,'viewfoo').__class__ is View )
        self.failUnless(T.publishTraverse(req,'foo') is foo)
        
        self.assertRaises(NotFoundError , T.publishTraverse, req, 'morebar')
        self.assertRaises(NotFoundError , T.publishTraverse, req,
                          '@@morebar')

       


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
