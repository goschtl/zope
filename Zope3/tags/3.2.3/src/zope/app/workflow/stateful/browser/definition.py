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


class RelevantDataSchemaEdit(EditView):

    def __init__(self, context, request):
        super(RelevantDataSchemaEdit, self).__init__(context, request)
        self.buildPermissionWidgets()

    def buildPermissionWidgets(self):
        schema = self.context.relevantDataSchema
        if schema is not None:
            for name, field in getFields(schema).items():

                if self.context.schemaPermissions.has_key(name):
                    get_perm, set_perm = self.context.schemaPermissions[name]
                    try:
                        get_perm_id = get_perm.id
                    except:
                        get_perm_id = None
                    try:
                        set_perm_id = set_perm.id
                    except:
                        set_perm_id = None
                else:
                    get_perm_id, set_perm_id = None, None

                # Create the Accessor Permission Widget for this field
                permField = Choice(
                    __name__=name+'_get_perm',
                    title=u"Accessor Permission",
                    vocabulary="Permission Ids",
                    default=CheckerPublic,
                    required=False)
                setUpWidget(self, name + '_get_perm', permField, IInputWidget, 
                            value=get_perm_id)

                # Create the Mutator Permission Widget for this field
                permField = Choice(
                    __name__=name+'_set_perm',
                    title=u"Mutator Permission",
                    default=CheckerPublic,
                    vocabulary="Permission Ids",
                    required=False)
                setUpWidget(self, name+'_set_perm', permField, IInputWidget, 
                            value=set_perm_id)

    def update(self):
        status = ''

        if Update in self.request:
            status = super(RelevantDataSchemaEdit, self).update()
            self.buildPermissionWidgets()
        elif 'CHANGE' in self.request:
            schema = self.context.relevantDataSchema
            perms = removeSecurityProxy(self.context.schemaPermissions)
            for name, field in getFields(schema).items():
                
                getPermWidget = getattr(self, name+'_get_perm_widget')
                setPermWidget = getattr(self, name+'_set_perm_widget')
                
                # get the selected permission id from the from request
                get_perm_id = getPermWidget.getInputValue()
                set_perm_id = setPermWidget.getInputValue()

                # get the right permission from the given id
                get_perm = zapi.getUtility(IPermission, get_perm_id)
                set_perm = zapi.getUtility(IPermission, set_perm_id)
                
                # set the permission back to the instance
                perms[name] = (get_perm, set_perm)

                # update widget ohterwise we see the old value
                getPermWidget.setRenderedValue(get_perm_id)
                setPermWidget.setRenderedValue(set_perm_id)
                
                
                
            status = 'Fields permissions mapping updated.'

        return status

    def getPermissionWidgets(self):
        schema = self.context.relevantDataSchema
        if schema is None:
            return None
        info = []
        for name, field in getFields(schema).items():
            field = removeSecurityProxy(field)
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
