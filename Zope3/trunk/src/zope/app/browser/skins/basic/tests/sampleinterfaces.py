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

$Id: sampleinterfaces.py,v 1.2 2002/12/25 14:12:41 jim Exp $
"""

from zope.interface import Interface

from zope.app.interfaces.traversing.traverser import ITraverser

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
