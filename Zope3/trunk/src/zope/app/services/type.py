##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""Persistent type registry

$Id: type.py,v 1.2 2004/02/20 16:57:30 fdrake Exp $
"""
__metaclass__ = type

from persistent import Persistent
from persistent.dict import PersistentDict
from zope.interface.type import TypeRegistry

class PersistentTypeRegistry(Persistent, TypeRegistry):

    def __init__(self):
        super(PersistentTypeRegistry, self).__init__(PersistentDict())
