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
"""ProcessDefinition registration adding view

$Id: definition.py,v 1.1 2004/04/24 23:18:24 srichter Exp $
"""
__metaclass__ = type

from zope.proxy import removeAllProxies
from zope.app.publisher.browser import BrowserView
from zope.app.container.browser.adding import Adding
from zope.app.form.browser.submit import Update
from zope.app.form.browser.editview import EditView
from zope.app.form.interfaces import IInputWidget
from zope.app.workflow.stateful.definition import State, Transition
from zope.schema import getFields, Choice

from zope.security.checker import CheckerPublic
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.app.form.utility import setUpWidget

class StatesContainerAdding(Adding):
    """Custom adding view for StatesContainer objects."""
    menu_id = "add_stateful_states"


class TransitionsContainerAdding(Adding):
    """Custom adding view for TransitionsContainer objects."""
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
        return super(StateAddFormHelper, self).__call__(template_usage,
                                                        *args, **kw)


class StatefulProcessDefinitionView(BrowserView):

    def getName(self):
        return """I'm a stateful ProcessInstance"""


class RelevantDataSchemaEdit(EditView):

    def __init__(self, context, request):
        super(RelevantDataSchemaEdit, self).__init__(context, request)
        self.buildPermissionWidgets()

    def buildPermissionWidgets(self):
        schema = self.context.relevantDataSchema
        if schema is not None:
            for name, field in getFields(schema).items():
                # Try to get current settings
                if self.context.schemaPermissions.has_key(name):
                    get_perm, set_perm = self.context.schemaPermissions[name]
                else:
                    get_perm, set_perm = None, None

                # Create the Accessor Permission Widget for this field
                permField = Choice(
                    __name__=name+'_get_perm',
                    title=u"Accessor Permission",
                    vocabulary="Permissions",
                    default=CheckerPublic,
                    required=False)
                setUpWidget(self, name + '_get_perm', permField, IInputWidget, 
                            value=get_perm)

                # Create the Mutator Permission Widget for this field
                permField = Choice(
                    __name__=name+'_set_perm',
                    title=u"Mutator Permission",
                    default=CheckerPublic,
                    vocabulary="Permissions",
                    required=False)
                setUpWidget(self, name+'_set_perm', permField, IInputWidget, 
                            value=set_perm)

    def update(self):
        status = ''

        if Update in self.request:
            status = super(RelevantDataSchemaEdit, self).update()
            self.buildPermissionWidgets()
        elif 'CHANGE' in self.request:
            schema = self.context.relevantDataSchema
            perms = trustedRemoveSecurityProxy(self.context.schemaPermissions)
            for name, field in getFields(schema).items():
                getPerm = getattr(
                    self, name+'_get_perm_widget').getInputValue()
                setPerm = getattr(
                    self, name+'_set_perm_widget').getInputValue()
                perms[name] = (getPerm, setPerm)
            status = 'Fields permissions mapping updated.'

        return status

    def getPermissionWidgets(self):
        schema = self.context.relevantDataSchema
        if schema is None:
            return None
        info = []
        for name, field in getFields(schema).items():
            field = trustedRemoveSecurityProxy(field)
            info.append(
                {'fieldName': name,
                 'fieldTitle': field.title,
                 'getter': getattr(self, name+'_get_perm_widget'),
                 'setter': getattr(self, name+'_set_perm_widget')} )
        return info


class AddState(BrowserView):

    def action(self, id):
        state = State()
        self.context[id] = state
        return self.request.response.redirect(self.request.URL[-2])


class AddTransition(BrowserView):

    # XXX This could and should be handled by a Vocabulary Field/Widget
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
