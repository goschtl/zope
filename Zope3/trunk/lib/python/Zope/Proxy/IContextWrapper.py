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
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""

Revision information:
$Id: IContextWrapper.py,v 1.2 2002/06/10 23:29:31 jim Exp $
"""
from Interface import Interface

class IContextWrapper(Interface):

    def ContextWrapper(object, parent, **data):
        """Create a context wrapper for object in parent

        If the object is in a security proxy, then result will will be
        a security proxy for the unproxied object in context.

        Consider an object, o1, in a proxy p1 with a checker c1.

        If we call ContextWrapper(p1, parent, name='foo'), then we'll
        get::

          Proxy(Wrapper(o1, parent, name='foo'), c1)
          
        """

    def getWrapperData(ob):
        """Get the context wrapper data for an object
        """

    def getWrapperContainer(ob):
        """Get the object's container, as computed from a context wrapper
        """

    def getWrapperContext(ob):
        """Get the object's context, as computed from a context wrapper
        """

    def ContainmentIterator(ob):
        """Get an iterator for the object's containment chain
        """

        
    
