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
"""ProcessDefinition configuration adding view
 
$Id: definition.py,v 1.1 2003/05/08 17:27:17 jack-e Exp $
"""
__metaclass__ = type

from zope.proxy.introspection import removeAllProxies
from zope.component import getServiceManager
from zope.publisher.browser import BrowserView
from zope.app.browser.container.adding import Adding
from zope.app.form.utility import setUpWidgets, getWidgetsDataForContent
from zope.app.interfaces.workflow.stateful import IStatefulProcessDefinition

from zope.app.workflow.stateful.definition import State, Transition

from zope.app.browser.form.submit import Update


class StatesContainerAdding(Adding):
    """Custom adding view for StatesContainer objects.
    """
    menu_id = "add_stateful_states"


class TransitionsContainerAdding(Adding):
    """Custom adding view for TransitionsContainer objects.
    """
    menu_id = "add_stateful_transitions"

    def getProcessDefinition(self):
        return self.context.getProcessDefinition()


# XXX Temporary ...
class StateAddFormHelper:

    # XXX Hack to prevent from displaying an empty addform
    def __call__(self, template_usage=u'', *args, **kw):
        if not len(self.fieldNames):
            self.request.form[Update] = 'submitted'
            return self.update()
        return super(StateAddFormHelper, self).__call__(template_usage, *args, **kw)



class StatefulProcessDefinitionView(BrowserView):
 
    def getName(self):
        return """I'm a stateful ProcessInstance"""



class AddState(BrowserView):

    def action(self, id):
        state = State()
        self.context.setObject(id, state)
        return self.request.response.redirect(self.request.URL[-2])


class AddTransition(BrowserView):

    def getStateNames(self):
        pd = self.context.getProcessDefinition()
        states = removeAllProxies(pd.getStateNames())
        states.sort()
        return states

    def action(self, id, source, destination, condition=None, permission=None):
        condition = condition or None
        permission = permission or None
        transition = Transition(source, destination, condition, permission)
        self.context.setObject(id, transition)
        return self.request.response.redirect(self.request.URL[-2])
