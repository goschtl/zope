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
from Interface import Interface
from Interface.Attribute import Attribute

class ITestClass(Interface):
    def drool():
        """...drool..."""
        
class BaseTestClass:
    """This is stupid base class"""
    pass

class TestClass(BaseTestClass):
    """This is my stupid doc string"""
    __implements__ = ITestClass
    def drool(self):
        pass
    
class I(Interface):
    """bah blah"""
    
class I2(I):
    """eek"""
    
class I3(I, I2):
    """This is dummy doc string"""
    
    testAttribute1 = Attribute("""This is a dummy attribute.""")
    testAttribute2 = Attribute("""This is a dummy attribute.""")
    
    def one(param):
        """method one"""

    def two(param1, param2):
        """method two"""
