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
"""Stateful Process Instance

$Id$
"""
from persistent import Persistent
from persistent.dict import PersistentDict

from zope.event import notify

from zope.app import zapi
from zope.app.module import resolve
from zope.app.workflow.interfaces import IProcessDefinition
from zope.app.workflow.stateful.interfaces import AUTOMATIC
from zope.app.workflow.stateful.interfaces import IAfterTransitionEvent
from zope.app.workflow.stateful.interfaces import IBeforeTransitionEvent
from zope.app.workflow.stateful.interfaces import IRelevantDataChangeEvent
from zope.app.workflow.stateful.interfaces import IStatefulProcessInstance
from zope.app.workflow.stateful.interfaces import ITransitionEvent
from zope.app.workflow.stateful.interfaces import IBeforeRelevantDataChangeEvent
from zope.app.workflow.stateful.interfaces import IAfterRelevantDataChangeEvent
from zope.app.servicenames import Utilities
from zope.app.traversing.api import getParent
from zope.app.workflow.instance import ProcessInstance
from zope.app.container.contained import Contained

from zope.security.interfaces import Unauthorized
from zope.interface import directlyProvides, implements
from zope.proxy import removeAllProxies
from zope.schema import getFields
from zope.security.management import queryInteraction
from zope.security.checker import CheckerPublic, Checker
from zope.security.proxy import Proxy
from zope.security import checkPermission
from zope.tales.engine import Engine


class TransitionEvent(object):
    """A simple implementation of the transition event."""
    implements(ITransitionEvent)

    def __init__(self, object, process, transition):
        self.object = object
        self.process = process
        self.transition = transition

class BeforeTransitionEvent(TransitionEvent):
    implements(IBeforeTransitionEvent)

class AfterTransitionEvent(TransitionEvent):
    implements(IAfterTransitionEvent)


class RelevantDataChangeEvent(object):
    """A simple implementation of the transition event."""
    implements(IRelevantDataChangeEvent)

    def __init__(self, process, schema, attributeName, oldValue, newValue):
        self.process = process
        self.schema = schema
        self.attributeName = attributeName
        self.oldValue = oldValue
        self.newValue = newValue

class BeforeRelevantDataChangeEvent(RelevantDataChangeEvent):
    implements(IBeforeRelevantDataChangeEvent)

class AfterRelevantDataChangeEvent(RelevantDataChangeEvent):
    implements(IAfterRelevantDataChangeEvent)


class RelevantData(Persistent, Contained):
    """The relevant data object can store data that is important to the
    workflow and fires events when this data is changed.

    If you don't understand this code, don't worry, it is heavy lifting.
    """

    def __init__(self, schema=None, schemaPermissions=None):
        super(RelevantData, self).__init__()
        self.__schema = None
        # Add the new attributes, if there was a schema passed in
        if schema is not None:
            for name, field in getFields(schema).items():
                setattr(self, name, field.default)
            self.__schema = schema
            directlyProvides(self, schema)

            # Build up a Checker rules and store it for later
            self.__checker_getattr = {}
            self.__checker_setattr = {}
            for name in getFields(schema):
                get_perm, set_perm = schemaPermissions.get(name, (None, None))
                self.__checker_getattr[name] = get_perm or CheckerPublic
                self.__checker_setattr[name] = set_perm or CheckerPublic

            # Always permit our class's two public methods
            self.__checker_getattr['getChecker'] = CheckerPublic
            self.__checker_getattr['getSchema'] = CheckerPublic


    def __setattr__(self, key, value):
        # The '__schema' attribute has a sepcial function
        if key in ('_RelevantData__schema',
                   '_RelevantData__checker_getattr',
                   '_RelevantData__checker_setattr',
                   'getChecker', 'getSchema') or \
               key.startswith('_p_'):
            return super(RelevantData, self).__setattr__(key, value)

        is_schema_field = (self.__schema is not None and 
                           key in getFields(self.__schema).keys())

        if is_schema_field:
            process = self.__parent__ 
            # Send an Event before RelevantData changes
            oldvalue = getattr(self, key, None)
            notify(BeforeRelevantDataChangeEvent(
                process, self.__schema, key, oldvalue, value))

        super(RelevantData, self).__setattr__(key, value)

        if is_schema_field:
            # Send an Event after RelevantData has changed
            notify(AfterRelevantDataChangeEvent(
                process, self.__schema, key, oldvalue, value))

    def getChecker(self):
        return Checker(self.__checker_getattr, self.__checker_setattr)

    def getSchema(self):
        return self.__schema


class StateChangeInfo(object):
    """Immutable StateChangeInfo."""

    def __init__(self, transition):
        self.__old_state = transition.sourceState
        self.__new_state = transition.destinationState

    old_state = property(lambda self: self.__old_state)

    new_state = property(lambda self: self.__new_state)


class StatefulProcessInstance(ProcessInstance, Persistent):
    """Stateful Workflow ProcessInstance."""

    implements(IStatefulProcessInstance)

    def getData(self):
        if self._data is None:
            return None
        # Always give out the data attribute as proxied object.
        return Proxy(self._data, self._data.getChecker())
        
    data = property(getData) 

    def initialize(self):
        """See zope.app.workflow.interfaces.IStatefulProcessInstance"""
        pd = self.getProcessDefinition()
        clean_pd = removeAllProxies(pd)
        self._status = clean_pd.getInitialStateName()

        # resolve schema class
        # This should really always return a schema
        schema = clean_pd.getRelevantDataSchema()
        if schema:
            # create relevant-data
            self._data = RelevantData(schema, clean_pd.schemaPermissions)
            self._data.__parent__ = self
        else:
            self._data = None
        # setup permission on data

        # check for Automatic Transitions
        self._checkAndFireAuto(clean_pd)

    def getOutgoingTransitions(self):
        """See zope.app.workflow.interfaces.IStatefulProcessInstance"""
        pd = self.getProcessDefinition()
        clean_pd = removeAllProxies(pd)
        return self._outgoingTransitions(clean_pd)

    def fireTransition(self, id):
        """See zope.app.workflow.interfaces.IStatefulProcessInstance"""
        pd = self.getProcessDefinition()
        clean_pd = removeAllProxies(pd)
        if not id in self._outgoingTransitions(clean_pd):
            raise KeyError, 'Invalid Transition Id: %s' % id
        transition = clean_pd.transitions[id]
        # Get the object whose status is being changed.
        obj = getParent(self)

        # Send an event before the transition occurs.
        notify(BeforeTransitionEvent(obj, self, transition))

        # change status
        self._status = transition.destinationState

        # Send an event after the transition occured.
        notify(AfterTransitionEvent(obj, self, transition))

        # check for automatic transitions and fire them if necessary
        self._checkAndFireAuto(clean_pd)

    def getProcessDefinition(self):
        """Get the ProcessDefinition object from Workflow Utility."""
        return zapi.getUtility(IProcessDefinition, self.processDefinitionName)

    def _getContext(self):
        ctx = {}
        # data should be readonly for condition-evaluation
        ctx['data'] = self.data
        ctx['principal'] = None
        interaction = queryInteraction()
        if interaction is not None:
            principals = [p.principal for p in interaction.participations]
            if principals:
                # There can be more than one principal
                assert len(principals) == 1
                ctx['principal'] = principals[0]

        # TODO This needs to be discussed:
        # how can we know if this ProcessInstance is annotated
        # to a Content-Object and provide secure ***READONLY***
        # Access to it for evaluating Transition Conditions ???

        #content = self.__parent__

        # TODO: How can i make sure that nobody modifies content
        # while the condition scripts/conditions are evaluated ????
        # this hack only prevents from directly setting an attribute
        # using a setter-method directly is not protected :((
        #try:
        #    checker = getChecker(content)
        #    checker.set_permissions = {}
        #except TypeError:
        #    # got object without Security Proxy
        #    checker = selectChecker(content)
        #    checker.set_permissions = {}
        #    content = Proxy(content, checker)

        #ctx['content'] = content

        return ctx


    def _extendContext(self, transition, ctx={}):
        ctx['state_change'] = StateChangeInfo(transition)
        return ctx

    def _evaluateCondition(self, transition, contexts):
        """Evaluate a condition in context of relevant-data."""
        if not transition.condition:
            return True
        expr = Engine.compile(transition.condition)
        return expr(Engine.getContext(contexts=contexts))

    def _evaluateScript(self, transition, contexts):
        """Evaluate a script in context of relevant-data."""
        script = transition.script
        if not script:
            return True
        if isinstance(script, (str, unicode)):
            # XXX: not tested!
            script = resolve(script)
        return script(contexts)

    def _outgoingTransitions(self, clean_pd):
        ret = []
        contexts = self._getContext()

        for name, trans in clean_pd.transitions.items():
            if self.status == trans.sourceState:
                # check permissions
                permission = trans.permission
                if not checkPermission(permission, self):
                    continue

                ctx = self._extendContext(trans, contexts)
                # evaluate conditions
                if trans.condition is not None:
                    try:
                      include = self._evaluateCondition(trans, ctx)
                    except Unauthorized:
                        include = 0
                    if not include:
                        continue

                if trans.script is not None:
                    try:
                        include = self._evaluateScript(trans, ctx)
                    except Unauthorized:
                        include = 0
                    if not include:
                        continue

                # append transition name
                ret.append(name)
        return ret

    def _checkAndFireAuto(self, clean_pd):
        outgoing_transitions = self.getOutgoingTransitions()
        for name in outgoing_transitions:
            trans = clean_pd.transitions[name]
            if trans.triggerMode == AUTOMATIC:
                self.fireTransition(name)
                return
