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

$Id: containmentiterator.py,v 1.2 2002/12/25 14:15:16 jim Exp $
"""

from zope.proxy.context import Wrapper, wrapperTypes, getinnercontext

class ContainmentIterator:

    def __init__(self, obj):
        self._ob = Wrapper(None, obj)

    def __iter__(self):
        return self

    def next(self):
        ob = self._ob
        if type(ob) not in wrapperTypes:
            raise StopIteration

        ob = getinnercontext(ob)
        self._ob = ob
        return ob
