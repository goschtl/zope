##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Stateful Process Instance

$Id: instance.py,v 1.1 2003/05/08 17:27:19 jack-e Exp $
"""
__metaclass__ = type

from types import StringTypes
from persistence import Persistent
from zope.schema import getFields
from zope.interface import directlyProvides

from zope.exceptions import Unauthorized

from zope.component import getService
from zope.component import getServiceManager

from zope.proxy.introspection import removeAllProxies
from zope.proxy.context import ContextMethod, getWrapperContainer
from zope.proxy.context import ContextWrapper,ContextAware

from zope.security.management import getSecurityManager
from zope.security.checker import CheckerPublic

# XXX Needed for WfrData Permission checking
# commented out for now
#from zope.security.checker import CheckerPublic, selectChecker
#from zope.security.checker import Checker
#from zope.security.proxy import getChecker, Proxy

from zope.app.security.permission import checkPermission

from zope.tales.engine import Engine

from zope.app.interfaces.workflow.stateful import IStatefulProcessInstance
from zope.app.workflow.instance import ProcessInstance



class RelevantData(ContextAware):
    pass

# XXX Example of how Changes to Workflow Relevant Data would send out Events
# ToDo:
# - Define Events:
#    RelevantDataChangingWorkflowEvent
#    RelevantDataChangedWorkflowEvent
#
# - all this is untested !!!!
#
#class RelevantData:
#
#    def __setattr__(self, key, value):
#        is_schema_field = bool(key in getFields(self.__implements__).keys())
#        if is_schema_field:
#            # Send an Event bevor RelevantData changes
#            oldvalue = getattr(self, key, None)
#            print "send RelevantDataChangingWorkflowEvent(key:%s, old:%s, new:%s) here" \
#                  % (key, oldvalue, value)
#
#        super(RelevantData, self).__setattr__(key, value)
#
#        if is_schema_field:
#            # Send an Event after RelevantData has changed
#            print "send RelevantDataChangedWorkflowEvent(key:%s, old:%s, new:%s) here" \
#                  % (key, oldvalue, value)




class StateChangeInfo:
    """Immutable StateChangeInfo.
    """

    def __init__(self, transition):
        self.__old_state = transition.sourceState
        self.__new_state = transition.destinationState

    old_state = property(lambda self: self.__old_state)

    new_state = property(lambda self: self.__new_state)



class StatefulProcessInstance(ProcessInstance, Persistent):
    """Stateful Workflow ProcessInstance.
    """

    __implements__ = IStatefulProcessInstance


    ############################################################
    # Implementation methods for interface
    # zope.app.interfaces.workflow.IStatefulProcessInstance



    data = property(lambda self: ContextWrapper(self._data, self))
    
    # XXX this is not entirely tested nor finished
    #def _getData(self):
    #    """getter for Workflow Relevant Data."""
    #    
    #    data = self._data
    #    if data is None:
    #        return
    #    
    #    schema = data.__implements__
    #
    #    # XXX permissions need to be manageable TTW
    #    # is this too much overhead ????
    #    checker_getattr = {}
    #    checker_setattr = {}
    #    for name in schema.names(all=True):
    #        
    #        # XXX Just a dummy implementation for now
    #        checker_getattr[name] = CheckerPublic
    #        checker_setattr[name] = CheckerPublic
    #        
    #    checker = Checker(checker_getattr.get, checker_setattr.get)
    #    return Proxy(data, checker)
    #
    #data = property(lambda self: ContextWrapper(self._getData(), self))

    
    def initialize(self):
        pd = self._getProcessDefinition()
        clean_pd = removeAllProxies(pd)
        self._status = clean_pd.getInitialStateName()

        # resolve schema class 
        schema = clean_pd.getRelevantDataSchema()
        if schema:
            if type(schema) in StringTypes:
                sm = getServiceManager(self)
                schema =  sm.resolve(schema)

            # create relevant-data
            self._data = self._buildRelevantData(schema)
        else:
            self._data = None
        # setup permission on data
        
        # check for Automatic Transitions
        self._checkAndFireAuto(clean_pd)
    initialize = ContextMethod(initialize)
        

    def getOutgoingTransitions(self):
        pd = self._getProcessDefinition()
        clean_pd = removeAllProxies(pd)
        return self._outgoingTransitions(clean_pd)
    getOutgoingTransitions = ContextMethod(getOutgoingTransitions)


    def fireTransition(self, id):
        pd = self._getProcessDefinition()
        clean_pd = removeAllProxies(pd)
        if not id in self._outgoingTransitions(clean_pd):
            raise KeyError, 'Invalid Transition Id: %s' % id
        trans = clean_pd.transitions[id]
        # modify relevant-data if needed

        # XXX Implement EventHandling in BaseClass as property ???
        # send StatusChangingWorkflowEvent
        #print "send StatusChangingWorkflowEvent(old:%s, new:%s) here" \
        #      % (self._status, trans.destinationState)
        
        # change status
        self._status = trans.destinationState

        # send StatusChangedWorkflowEvent
        #print "send StatusChangedWorkflowEvent(old:%s, new:%s) here" \
        #      % (trans.sourceState, self._status)


        # check for automatic transitions
        self._checkAndFireAuto(clean_pd)
    fireTransition = ContextMethod(fireTransition)

    #
    ############################################################
    
    # XXX expose this method in the interface (without _) ???
    def _getProcessDefinition(self):
        """Get the ProcessDefinition object from WorkflowService.
        """
        svc =  getService(self, "Workflows")
        return svc.getProcessDefinition(self.processDefinitionName)
    _getProcessDefinition = ContextMethod(_getProcessDefinition)



    # XXX this is not entirely tested
    def _getContext(self):
        ctx = {}
        # data should be readonly for condition-evaluation
        ctx['data'] = self.data
        ctx['principal'] = getSecurityManager().getPrincipal()

        # XXX This needs to be discussed:
        # how can we know if this ProcessInstance is annotated
        # to a Content-Object and provide secure ***READONLY***
        # Access to it for evaluating Transition Conditions ???
        
        #content = getWrapperContainer(self)

        # XXX How can i make shure that nobody modifies content
        # while the condition scripts/conditions are evaluated ????
        # this hack only prevents from directly setting an attribute
        # using a setter-method directly is not protected :((
        #try:
        #    checker = getChecker(content)
        #    checker._setattr_permission_func = lambda x: None
        #except TypeError:
        #    # got object without Security Proxy
        #    checker = selectChecker(content)
        #    checker._setattr_permission_func = lambda x: None
        #    content = Proxy(content, checker)

        #ctx['content'] = content
        
        return ctx

    _getContext = ContextMethod(_getContext)


    def _extendContext(self, transition, ctx={}):
        ctx['state_change'] = StateChangeInfo(transition)
        return ctx

    
    def _evaluateCondition(self, transition, contexts):
        """Evaluate a condition in context of relevant-data.
        """
        if not transition.condition:
            return True
        expr = Engine.compile(transition.condition)
        return expr(Engine.getContext( contexts=contexts ))


    def _evaluateScript(self, transition, contexts):
        script = transition.script
        if not script:
            return True
        if type(script) in StringTypes:
            sm = getServiceManager(self)
            script =  sm.resolve(script)
        return script(contexts)
    _evaluateScript = ContextMethod(_evaluateScript)


    def _buildRelevantData(self, schema):
        """Create a new data object and initialize with Schema defaults.
        """
        data = RelevantData()
        if schema is not None:
            # set schema to RelevantData Instance
            directlyProvides(data, schema)
            for name, field in getFields(schema).items():
                setattr(data, name, field.default)
        return data


    def _outgoingTransitions(self, clean_pd):
        sm = getSecurityManager()
        ret = []
        contexts = self._getContext()
        
        for name, trans in clean_pd.transitions.items():
            if self.status == trans.sourceState:
                # check permissions
                permission = trans.permission
                # 
                if (permission is not None
                    and permission is not CheckerPublic
                    and not sm.checkPermission(permission, self)
                    ):
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
    _outgoingTransitions = ContextMethod(_outgoingTransitions)
        

    def _checkAndFireAuto(self, clean_pd):
        outgoing_transitions = self.getOutgoingTransitions()
        for name in outgoing_transitions:
            trans = clean_pd.transitions[name]
            # XXX Use Constants instead of strings
            if trans.triggerMode == 'Automatic':
                self.fireTransition(name)
                return
    _checkAndFireAuto = ContextMethod(_checkAndFireAuto)

