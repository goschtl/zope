##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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

$Id: testadapter.py 41271 2006-01-11 17:02:07Z oestermeier $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component
import zorg.usage

# Define some test interfaces

class INumber(zope.interface.Interface) :

    def number() :
        pass
    
class IFirst(INumber) :
    pass
    
class ISecond(INumber) :
    pass
    
class IIncrement(zope.interface.Interface) :
    
    def incr() :
        pass
        
class ICount(zope.interface.Interface) :

    def count() : 
        pass

# Define some trivial base classes

class First(object) :

    zope.interface.implements(IFirst)
    
    def number(self) :
        return 1

class Second(object) :

    zope.interface.implements(ISecond)
    
    def number(self) :
        return 2

# Define some adapter

class Increment(object) :
    """ A simple sample adapter. """
    
    zope.interface.implements(IIncrement)
    zope.component.adapts(INumber)
    
    zorg.usage.adapter()
    
    def __init__(self, context) :
        self.context = context
        
    def incr(self) :
        return self.context.number() + 1


class Count(object) :
    """ A multiadapter. """

    zope.interface.implements(ICount)
    zope.component.adapts(IFirst, ISecond)
    
    zorg.usage.adapter()

    def __init__(self, first, second) :
        self.first = first
        self.second = second

    def count(self) :
        print self.first.number()
        print self.second.number()
       
class Named(object) :
    """ A named adapter. """
    
