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
""" Addables """

from Zope.ComponentArchitecture import getService

def getAddableContent(wrapped_container):
    """return the list of content addables for the given container"""
    return getService(wrapped_container, 
                      'AddableContent').getAddables(wrapped_container)

def getAddableServices(wrapped_container):
    """return the list  of service addables for the given container"""
    return getService(wrapped_container,
                      'AddableServices').getAddables(wrapped_container)