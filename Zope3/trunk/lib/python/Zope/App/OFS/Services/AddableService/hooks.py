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
generic AddableContentService

$Id: hooks.py,v 1.2 2002/06/10 23:28:10 jim Exp $
"""
from Zope.ComponentArchitecture import getService

# hookables

def getAddableContent(context):
    """return the list of content addables for the given context"""
    return getAddableContent_hook(context)

def getAddableServices(context):
    """return the list  of service addables for the given context"""
    return getAddableServices_hook(context)

# hooks (rely on getService for placeful functionality)

def getAddableContent_hook(context):
    """return the list of content addables for the given context"""
    return getService(context, 'AddableContent').getAddables(context)

def getAddableServices_hook(context):
    """return the list  of service addables for the given context"""
    return getService(context, 'AddableServices').getAddables(context)