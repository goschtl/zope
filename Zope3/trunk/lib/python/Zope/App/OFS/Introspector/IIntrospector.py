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

class IIntrospector(Interface):
    """An interface for introspecting a component"""

    def isInterface():
        "Checks if the context is class or interface"
        
    def setRequest(request):
        """sets the request"""
        
    def getClass():
        """Returns the class name"""

    def getBaseClassNames():
        """Returns the names of the classes"""
        
    def getModule():
        """Returns the module name of the class"""
    
    def getDocString():
        """Returns the description of the class"""
        
    def getInterfaces():
        """Returns interfaces implemented by this class"""

    def getInterfaceNames():
        """Returns the name of the interface"""
        
    def getInterfaceDetails():
        """Returns the entire documentation in the interface"""

    def getExtends():
        """Returns all the class extended up to the top most level"""

    def getInterfaceConfiguration():
        """Returns details for a interface configuration"""        

