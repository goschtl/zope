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
"""Implementation of workflow process instance.

$Id: instance.py,v 1.1 2003/05/08 17:27:18 jack-e Exp $
"""
__metaclass__ = type

from types import StringTypes
from persistence import Persistent
from persistence.dict import PersistentDict
from zope.proxy.context import ContextWrapper
from zope.proxy.introspection import removeAllProxies

from zope.app.interfaces.annotation import IAnnotatable, IAnnotations
from zope.app.interfaces.workflow \
     import IProcessInstance, IProcessInstanceContainer

from zope.component import getAdapter

# XXX should an Instance be persistent by default ???
class ProcessInstance:

    __doc__ = IProcessInstance.__doc__

    __implements__ =  IProcessInstance

    def __init__(self, pd_name):
        self._pd_name = pd_name
        self._status = None
  
    
    ############################################################
    # Implementation methods for interface
    # zope.app.interfaces.workflow.IProcessInstance


    processDefinitionName = property(lambda self: self._pd_name)

    status = property(lambda self: self._status)


    #
    ############################################################


    ## should probably have a method "getProcessDefinition"








_marker = object()

WFKey = "zope.app.worfklow.ProcessInstanceContainer"

class ProcessInstanceContainerAdapter:

    __implements__ = IProcessInstanceContainer

    __used_for__ = IAnnotatable

    def __init__(self, context):
        self.context = context
        annotations = getAdapter(context, IAnnotations)
        wfdata = annotations.get(WFKey)
        if not wfdata:
            wfdata = PersistentDict()
            annotations[WFKey] = wfdata
        self.wfdata = wfdata

    def __getitem__(self, key):
        "See IProcessInstanceContainer"
        value = self.wfdata[key]
        return ContextWrapper(value, self.context, name=key)
 
    def get(self, key, default=None):
        "See IProcessInstanceContainer"
        value = self.wfdata.get(key, _marker)
        if value is not _marker:
            return ContextWrapper(value, self.context, name=key)
        else:
            return default
 
    def __contains__(self, key):
        "See IProcessInstanceContainer"
        return key in self.wfdata
 
 
    def values(self):
        "See IProcessInstanceContainer"
        container = self.wfdata
        result = []
        for key, value in container.items():
            result.append(ContextWrapper(value, self.context, name=key))
        return result
 
    def keys(self):
        "See IProcessInstanceContainer"
        return self.wfdata.keys()
 
    def __len__(self):
        "See IProcessInstanceContainer"
        return len(self.wfdata)
 
    def items(self):
        "See IProcessInstanceContainer"
        container = self.wfdata
        result = []
        for key, value in container.items():
            result.append((key, ContextWrapper(value, self.context, name=key)))
        return result
    
    def setObject(self, key, object):
        "See IProcessInstanceContainer"
 
        if not isinstance(key, StringTypes):
            raise TypeError("Item name is not a string.")
 
        container = self.wfdata
        object = removeAllProxies(object)
        container[key] = object
        # publish event ??
        return key
 
 
    def __delitem__(self, key):
        "See IZopeWriteContainer"
        container = self.wfdata
        # publish event ?
        del container[key]
        return key

    def __iter__(self):
        '''See interface IReadContainer'''
        return iter(self.context)

