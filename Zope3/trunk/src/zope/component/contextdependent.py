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
"""A simple mix-in class that implements IContextDependent. 

$Id: contextdependent.py,v 1.4 2004/02/20 20:35:33 srichter Exp $
"""
from zope.component.interfaces import IContextDependent
from zope.interface import implements

class ContextDependent(object):
    """standard boilerplate for context dependent objects"""

    implements(IContextDependent)

    def __init__(self, context):
        self.context = context
