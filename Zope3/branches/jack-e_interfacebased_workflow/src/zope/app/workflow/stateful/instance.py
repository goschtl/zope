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

from zope.app import zapi
from zope.event import notify
from zope.app.workflow.interfaces import IProcessDefinition
from zope.app.workflow.stateful.interfaces import AUTOMATIC
from zope.app.workflow.stateful.interfaces import ITransitionEvent
from zope.app.workflow.stateful.interfaces import IAfterTransitionEvent
from zope.app.workflow.stateful.interfaces import IBeforeTransitionEvent
from zope.app.workflow.stateful.interfaces import IStatefulPIAdapter

from zope.app.servicenames import Utilities
from zope.app.traversing.api import getParent
from zope.app.workflow.instance import PIAdapter
from zope.app.container.contained import Contained

from zope.security.interfaces import Unauthorized
from zope.interface import directlyProvides, implements
from zope.interface import directlyProvidedBy
from zope.proxy import removeAllProxies
from zope.security.proxy import removeSecurityProxy
from zope.schema import getFields
from zope.security.management import queryInteraction
from zope.security.checker import CheckerPublic, Checker
from zope.security.proxy import Proxy
from zope.security import checkPermission
from zope.tales.engine import Engine


class TransitionEvent(object):
    """A simple implementation of the transition event."""
    implements(ITransitionEvent)

    def __init__(self, context, transition):
        self.context = context
        self.transition = transition

class BeforeTransitionEvent(TransitionEvent):
    implements(IBeforeTransitionEvent)

class AfterTransitionEvent(TransitionEvent):
    implements(IAfterTransitionEvent)







class StateChangeInfo(object):
    """Immutable StateChangeInfo."""

    def __init__(self, transition):
        self.__old_state = transition.sourceState
        self.__new_state = transition.destinationState

    old_state = property(lambda self: self.__old_state)

    new_state = property(lambda self: self.__new_state)




class StatefulPIAdapter(PIAdapter):
    """Stateful Workflow ProcessInstance Adapter."""

    implements(IStatefulPIAdapter)

    def initialize(self):
        """See zope.app.workflow.interface.IStatefulProcessInstance"""
        clean_pd = removeAllProxies(self.processDefinition)

        # check for Automatic Transitions
        self._checkAndFireAuto(clean_pd)
        


    def getOutgoingTransitions(self):
        """See zope.app.workflow.interfaces.IStatefulProcessInstance"""
        clean_pd = removeAllProxies(self.processDefinition)
        return self._outgoingTransitions(clean_pd)


    # XXX API change here !!!
    def fireTransition(self, trans_id, event=None):
        """See zope.app.workflow.interfaces.IStatefulProcessInstance"""
        
        clean_pd = removeAllProxies(self.processDefinition)
        if not trans_id in self._outgoingTransitions(clean_pd, event):
            raise KeyError, 'Invalid Transition Id: %s' % trans_id
        transition = clean_pd.transitions[trans_id]
        
        # Get the object whose status is being changed.
        obj = removeSecurityProxy(self.context)

        # Send an event before the transition occurs.
        notify(BeforeTransitionEvent(obj, transition))

        # XXX Jim suggests to send out ObjectStateChanging/Changed Events instead
        # of Before/AfterTransition. Need to check the side effects (Phase2)
        
        # change status
        # XXX change self.context to implement the new interface
        # and remove the old state's interface

        oldStateIF = clean_pd.states[transition.sourceState].targetInterface
        newStateIF = clean_pd.states[transition.destinationState].targetInterface

        directlyProvides(obj, directlyProvidedBy(obj) + newStateIF - oldStateIF)

        # Send an event after the transition occured.
        notify(AfterTransitionEvent(obj, transition))

        # check for automatic transitions and fire them if necessary
        self._checkAndFireAuto(clean_pd)



    def _getContext(self, context={}):
        # data should be readonly for condition-evaluation
        context['principal'] = None
        interaction = queryInteraction()
        if interaction is not None:
            principals = [p.principal for p in interaction.participations]
            if principals:
                # There can be more than one principal
                assert len(principals) == 1
                context['principal'] = principals[0]

        content = removeSecurityProxy(self.context)
        context['content'] = content

        return context


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
            sm = zapi.getServices(self)
            script = sm.resolve(script)
        return script(contexts)


    def _outgoingTransitions(self, clean_pd, event=None):
        ret = []
        contexts = self._getContext({'event':event})

        # XXX
        context = removeSecurityProxy(self.context)
        context_spec = directlyProvidedBy(context)

        for name, trans in clean_pd.transitions.items():
            if context_spec.extends(clean_pd.states[trans.sourceState].targetInterface):
                # check permissions
                permission = trans.permission
                if not checkPermission(permission, context):
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


def initializeStatefulProcessFor(obj, pd_name):
    """provide a component and a processdefinition_name and
       to give that component behaviour.
    """
    # XXX For now we just add an attribute to the component
    # to remember which processdefinition specifies the behaviour.
    # This solution is not final and does not support multiple
    # processes for the same component. A smarter solution using
    # named Adapters providing (IProcessDefinition, [name])
    # for (ISomeStatefulProcess, ISomeContentType)
    obj.__processdefinition_name__ = pd_name
    
    pd = zapi.getUtility(IProcessDefinition, pd_name)
    clean_pd = removeAllProxies(pd)
    
    # XXX Jim suggests to send out ObjectStateChanging/Changed Events here (Phase2)
    
    # XXX Set Initial Interface to self.context here !!!
    directlyProvides(obj, pd.states[pd.getInitialStateName()].targetInterface)

    IStatefulPIAdapter(obj).initialize()
