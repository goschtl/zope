##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Implementation of workflow process instance.

$Id$
"""
from types import StringTypes
from persistent.dict import PersistentDict
from zope.proxy import removeAllProxies

from zope.interface import providedBy

from zope.app import zapi
from zope.app.annotation.interfaces import IAnnotatable, IAnnotations
from zope.app.container.interfaces import IContained
from zope.app.servicenames import Utilities, Adapters
from zope.app.workflow.interfaces import IPIAdapter, IProcessDefinition

from zope.interface import implements



class PIAdapter(object):
    """Adapter to interpret ProcessDefinitions with ContentObjects as Context.

    """
    implements(IPIAdapter)

    def __init__(self, context):
        self.context = context

    def _getProcessDefinition(self):
        # we have an Interface (ISomeState) that represents the actual
        # state of the object and extends our IMyProcessInstance Interface.
        # we should register the ProcessDefinition as an Adapter for IMyProcessInstance
        #return zapi.getService(Adapters).lookup([...how to define this?...],
        #                                        IProcessDefinition, '', None)
        
        # XXX but for now we just use the __processdefinition_name__ attribute on components.
        pd_name = getattr(removeAllProxies(self.context), '__processdefinition_name__', '')
        return zapi.getUtility(IProcessDefinition, pd_name)
    
    processDefinition = property(_getProcessDefinition)



