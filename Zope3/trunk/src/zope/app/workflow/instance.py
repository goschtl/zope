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

$Id$
"""
from types import StringTypes
from persistent.dict import PersistentDict
from zope.proxy import removeAllProxies

from zope.app import zapi
from zope.app.annotation.interfaces import IAnnotatable, IAnnotations
from zope.app.servicenames import Utilities
from zope.app.workflow.interfaces import IProcessInstance, IProcessDefinition
from zope.app.workflow.interfaces import IProcessInstanceContainer

from zope.interface import implements

from zope.app.container.contained import Contained, setitem, uncontained

# XXX should an Instance be persistent by default ???
class ProcessInstance(Contained):

    __doc__ = IProcessInstance.__doc__

    implements(IProcessInstance)

    def __init__(self, pd_name):
        self._pd_name = pd_name
        self._status = None

    processDefinitionName = property(lambda self: self._pd_name)

    status = property(lambda self: self._status)

    ## should probably have a method "getProcessDefinition"


def createProcessInstance(context, name):
    """Helper function to create a process instance from a process definition
    name."""
    utils = zapi.getService(Utilities, context)
    pd = utils.getUtility(IProcessDefinition, name)
    return pd.createProcessInstance(name)


_marker = object()

WFKey = "zope.app.worfklow.ProcessInstanceContainer"

class ProcessInstanceContainerAdapter(object):

    implements(IProcessInstanceContainer)

    __used_for__ = IAnnotatable

    def __init__(self, context):
        self.context = context
        # XXX: Band-aid, so that the process instance can have a valid
        # path. Eventually the pi should have context as parent directly. 
        self.__parent__ = context
        self.__name__ = "processInstances"
        annotations = IAnnotations(context)
        wfdata = annotations.get(WFKey)
        if not wfdata:
            wfdata = PersistentDict()
            annotations[WFKey] = wfdata
        self.wfdata = wfdata

    def __getitem__(self, key):
        "See IProcessInstanceContainer"
        value = self.wfdata[key]
        return value

    def get(self, key, default=None):
        "See IProcessInstanceContainer"
        value = self.wfdata.get(key, _marker)
        if value is not _marker:
            return value
        else:
            return default

    def __contains__(self, key):
        "See IProcessInstanceContainer"
        return key in self.wfdata

    def values(self):
        "See IProcessInstanceContainer"
        return self.wfdata.values()

    def keys(self):
        "See IProcessInstanceContainer"
        return self.wfdata.keys()

    def __len__(self):
        "See IProcessInstanceContainer"
        return len(self.wfdata)

    def items(self):
        "See IProcessInstanceContainer"
        return self.wfdata.items()

    def __setitem__(self, key, object):
        "See IProcessInstanceContainer"
        setitem(self, self.wfdata.__setitem__, key, object)

    def __delitem__(self, key):
        "See IZopeWriteContainer"
        container = self.wfdata
        # publish event ?
        uncontained(container[key], self, key)
        del container[key]

    def __iter__(self):
        '''See interface IReadContainer'''
        return iter(self.wfdata)

