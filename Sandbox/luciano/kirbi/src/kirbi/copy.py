##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Kirbi book exemplar class
"""

import grok
from interfaces import ICopy, ILease
from zope.interface import Interface, implements, invariant
from zope import schema

class Copy(grok.Container):
    """An exemplar of a book.
    
    A copy is associated to a Book instance.
    
    A copy can contain Lease instances, recording each time it was lent.
    When a copy is transferred or deleted, the lease history automatically
    goes with it.
    """

    implements(ICopy)
    
    def __init__(self, book_id):
        super(User, self).__init__()
        
