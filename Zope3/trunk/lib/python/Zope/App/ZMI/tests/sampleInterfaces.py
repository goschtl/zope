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

$Id: sampleInterfaces.py,v 1.2 2002/06/10 23:29:19 jim Exp $
"""

from Interface import Interface

from Zope.App.Traversing.ITraverser import ITraverser

class FakeTraverser:

    __implements__ = ITraverser

    def __init__(self, *args, **kw): pass

    def traverse(self, *args, **kw):
        return None


class I1(Interface): pass
class I2(I1): pass

class O1:
    __implements__ = I1
    
class O2:
    __implements__ = I2    
