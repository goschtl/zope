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

Revision information:
$Id: testIntrospector.py,v 1.3 2002/07/17 16:54:18 jeremy Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

from Zope.App.OFS.Introspector.Introspector import Introspector

from Interface import Interface
from Interface.Implements import implements

class IStupid(Interface):
    
    def drool():
        """...drool..."""

class Stupid:
    """This is my stupid doc string"""
    def drool(self):
        pass

implements(Stupid, IStupid)

class Test(CleanUp, TestCase):
    
    def testDocString(self):
        intro=Introspector(Stupid())
        assert intro.getDocString()=="This is my stupid doc string"
        
    def testGetInterfaces(self):
        intro=Introspector(Stupid()).getInterfaces()
        assert (len(intro)==1 and intro[0]==IStupid)
        
    def testGetName(self):
        nm=Introspector(Stupid()).getName()
        assert nm=="Stupid"
    
    def testGetInterfaceNames(self):
        iname =  Introspector(Stupid()).getInterfaceNames()[0].split(".")
        i = __import__(iname[-2], globals(), locals(), iname[:-2])
        assert i.IStupid==IStupid

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
