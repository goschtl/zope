##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""IKeyreference adapter for zalchemy objects

$Id$
"""
__docformat__ = "reStructuredText"

from zope import interface, component
import zope.app.keyreference.interfaces
from zope.security.proxy import removeSecurityProxy
from z3c.zalchemy.interfaces import IMappedSQLAlchemyObject
class RefToMappedSQLAlchemyObject(object):
    
    """An IKeyReference for objects stored in an sql database by
    zalchemy whith a mapper attached to the class"""
    
    interface.implements(zope.app.keyreference.interfaces.IKeyReference)
    component.adapts(IMappedSQLAlchemyObject)

    key_type_id = 'z3c.zalchemy.intid.keyreference'

    def __init__(self, object):
        object =  removeSecurityProxy(object)
        self.ident = object.mapper.instance_key(object)[:2]
        self._class,self.pk = self.ident
        
    def __call__(self):
        return self._class.mapper.get(*self.pk)

    def __hash__(self):
        return hash(self.ident)
    
    def __cmp__(self, other):
        if self.key_type_id == other.key_type_id:
            return cmp(self.ident,other.ident)
        return cmp(self.key_type_id, other.key_type_id)




