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
""" Register class directive.

$Id: fsdirective.py,v 1.2 2003/05/05 18:01:01 gvanrossum Exp $
"""
from zope.app.fssync.fsregistry import provideSynchronizer
from zope.configuration.action import Action

def registerFSRegistry(_context, class_=None, factory=None):
    """registerFSRegistry method to register Class and Serializer factory
    associated with it.
    """
    cls = None
    if class_ is not None:
       cls = _context.resolve(class_)
    
    fct = _context.resolve(factory)

    return [Action(discriminator=('adapter', class_),
                   callable=provideSynchronizer,
                   args=(cls, fct))]
