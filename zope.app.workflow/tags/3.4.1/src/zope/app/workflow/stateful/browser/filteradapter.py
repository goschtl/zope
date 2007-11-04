##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""filtering view for ProcessInstances of a stateful workflow
 
$Id$
"""
from zope.interface import implements
from zope.app.workflow.interfaces import IProcessInstanceContainerAdaptable
from zope.app.workflow.interfaces import IProcessInstanceContainer

from interfaces import IContentFilterAdapter

class FilterAdapter(object):
    
    __used_for__ = IProcessInstanceContainerAdaptable
    implements(IContentFilterAdapter)

    def __init__(self, context):
        self.context = context

    def filterListByState(self, objList, state, workflow='default'):
        """See IContentFilterAdapter"""
        res = []

        for obj in objList:
            if self.filterObjectByState(obj, state, workflow):
                res.append(obj)

        return res

    def filterObjectByState(self, object, state, workflow='default'):
        """See IContentFilterAdapter"""
        adapter = IProcessInstanceContainer(object, None)
        if not adapter:
            return False
            
        for item in adapter.values():
            if item.processDefinitionName != workflow:
                continue
            if item.status == state:
                return True

        return False                
