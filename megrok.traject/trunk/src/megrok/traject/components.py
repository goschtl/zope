##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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

"""megrok.traject components"""

import grok
import traject

class Traject(object):
    grok.baseclass()

    pattern = None
    model = None
    
    def factory(**kw):
        raise NotImplementedError

    def arguments(obj):
        return NotImplementedError

class TrajectTraverser(grok.Traverser):
    grok.baseclass()
        
    def traverse(self, name):
        stack = self.request.getTraversalStack()
        stack.append(name)
        unconsumed, obj = traject.consume_stack(
            self.context, stack, DefaultModel)
        # if we haven't consumed *anything* we can't traverse, fall back
        if obj is self.context:
            return None
        self.request.setTraversalStack(unconsumed)
        return obj

class DefaultModel(grok.Model):
    def __init__(self, **kw):
        self.kw = kw
