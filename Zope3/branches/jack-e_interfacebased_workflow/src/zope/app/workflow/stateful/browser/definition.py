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
"""ProcessDefinition registration adding view

$Id$
"""
from zope.app import zapi
from zope.proxy import removeAllProxies
from zope.app.publisher.browser import BrowserView
from zope.app.container.browser.adding import Adding
from zope.app.form.browser.submit import Update
from zope.app.form.browser.editview import EditView
from zope.app.form.interfaces import IInputWidget
from zope.app.workflow.stateful.definition import State, Transition
from zope.schema import getFields, Choice

from zope.app.security.interfaces import IPermission
from zope.security.checker import CheckerPublic
from zope.security.proxy import removeSecurityProxy
from zope.app.form.utility import setUpWidget

class StatefulProcessDefinitionEdit(object):
    """ Custom adding for StatefulProcessDefinitions. """

    def changed(self):
        # XXX provide Adapter for this instance
        print "REGISTER ADAPTER" 
        

class StatesContainerAdding(Adding):
    """Custom adding view for StatesContainer objects."""
    menu_id = "add_stateful_states"


class TransitionsContainerAdding(Adding):
    """Custom adding view for TransitionsContainer objects."""
    menu_id = "add_stateful_transitions"

    def getProcessDefinition(self):
        return self.context.getProcessDefinition()


# TODO: Temporary ...
class StateAddFormHelper(object):
    # Hack to prevent from displaying an empty addform
    def __call__(self, template_usage=u'', *args, **kw):
        if not len(self.fieldNames):
            self.request.form[Update] = 'submitted'
            return self.update()
        return super(StateAddFormHelper, self).__call__(template_usage,
                                                        *args, **kw)


class StatefulProcessDefinitionView(BrowserView):

    def getName(self):
        return """I'm a stateful ProcessInstance"""



class AddState(BrowserView):

    def action(self, id):
        state = State()
        self.context[id] = state
        return self.request.response.redirect(self.request.URL[-2])


class AddTransition(BrowserView):

    # TODO: This could and should be handled by a Vocabulary Field/Widget
    def getStateNames(self):
        pd = self.context.getProcessDefinition()
        states = removeAllProxies(pd.getStateNames())
        states.sort()
        return states

    def action(self, id, source, destination, condition=None, permission=None):
        condition = condition or None
        permission = permission or None
        transition = Transition(source, destination, condition, permission)
        self.context[id] = transition
        return self.request.response.redirect(self.request.URL[-2])
