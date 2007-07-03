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

from zope.app import zapi
from zope.app.annotation.interfaces import IAnnotatable, IAnnotations
from zope.app.container.interfaces import IContained
from zope.app.workflow.interfaces import IProcessInstance, IProcessDefinition
from zope.app.workflow.interfaces import IProcessInstanceContainer

from zope.interface import implements

from zope.app.container.contained import Contained, setitem, uncontained

class ProcessInstance(Contained):
    """Process Instance implementation.

    Process instances are always added to a process instance container. This
    container lives in an annotation of the object and is commonly stored in
    the ZODB. Therefore a process instance should be persistent.
    """
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
    sm = zapi.getSiteManager(context)
    pd = sm.queryUtility(IProcessDefinition, name)
    return pd.createProcessInstance(name)


_marker = object()

WFKey = "zope.app.worfklow.ProcessInstanceContainer"

class ProcessInstanceContainerAdapter(object):

    implements(IProcessInstanceContainer)

    __used_for__ = IAnnotatable

    def __init__(self, context):
        self.context = context
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
        # We cannot make the message the parent right away, since it is not
        # added to any message board yet;
        setitem(self, self.wfdata.__setitem__, key, object)
        # Set the final parent to be the message.
        if IContained.providedBy(object):
            object.__parent__ = self.context

    def __delitem__(self, key):
        "See IZopeWriteContainer"
        container = self.wfdata
        # publish event ?
        uncontained(container[key], self, key)
        del container[key]

    def __iter__(self):
        '''See interface IReadContainer'''
        return iter(self.wfdata)

