##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Content Component Views

$Id$
"""
import copy
from zope.app import zapi
from zope.app.form.browser.add import AddView
from zope.app.form.browser.editview import EditView
from zope.app.form.browser.submit import Update
from zope.app.form.utility import setUpWidget
from zope.app.form.interfaces import IInputWidget
from zope.app.schemacontent.interfaces import IContentComponentDefinition
from zope.app.schemacontent.content import ContentComponentInstance
from zope.component.exceptions import ComponentLookupError
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.schema import getFieldsInOrder, Choice
from zope.security.checker import CheckerPublic
from zope.security.proxy import removeSecurityProxy

class ContentComponentPermissionEdit(EditView):

    def __init__(self, context, request):
        super(ContentComponentPermissionEdit, self).__init__(context, request)
        self.buildPermissionWidgets()

    def buildPermissionWidgets(self):
        schema = self.context.schema
        for name, field in getFieldsInOrder(schema):
            
            # get the permissions and then the permission id.
            # We can't deal in dropdownboxes with permission itself.
            # There is no way to compare the permission to the
            # "Permission" or "Permission Id" vocabulary for to
            # get the SELECTED state.
            if self.context.permissions.has_key(name):
                get_perm, set_perm = self.context.permissions[name]
                try:
                    get_perm_id = get_perm.id
                    print 'get_perm.id = %s' % get_perm.id
                except:
                    get_perm_id = None
                try:
                    set_perm_id = set_perm.id
                    print 'set_perm.id = %s' % set_perm.id
                except:
                    set_perm_id = None
            else:
                get_perm_id, set_perm_id = None, None
            
            # Create the Accessor Permission Widget for this field
            permField = Choice(
                __name__=name+'_get_perm',
                title=u"Accessor Permission",
                default=CheckerPublic,
                vocabulary="Permission Ids",
                required=False)
            setUpWidget(self, name+'_get_perm', permField, IInputWidget,
                        value=get_perm_id, ignoreStickyValues=True)

            # Create the Mutator Permission Widget for this field
            permField = Choice(
                __name__=name+'_set_perm',
                title=u"Mutator Permission",
                default=CheckerPublic,
                vocabulary="Permission Ids",
                required=False)
            setUpWidget(self, name+'_set_perm', permField, IInputWidget,
                        value=set_perm_id, ignoreStickyValues=True)

    def update(self):
        status = ''

        if Update in self.request:
            status = super(ContentComponentPermissionEdit, self).update()
            self.buildPermissionWidgets()
        elif 'CHANGE' in self.request:
            schema = self.context.schema
            perms = removeSecurityProxy(self.context.permissions)
            for name, field in getFieldsInOrder(schema):
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
        schema = self.context.schema
        info = []
        for name, field in getFieldsInOrder(schema):
            field = removeSecurityProxy(field)
            info.append(
                {'fieldName': name,
                 'fieldTitle': field.title,
                 'getter': getattr(self, name+'_get_perm_widget'),
                 'setter': getattr(self, name+'_set_perm_widget')} )
        return info


class AddContentComponentInstanceView(AddView):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        """See zope.app.container.interfaces.IAdding"""
        if '=' in name:
            type_name, content_name = name.split("=", 1)
            self.context.contentName = content_name

        matching = [util
                    for name, util in zapi.getUtilitiesFor(
                                                  IContentComponentDefinition)
                    if name == type_name]
            
        if not matching:
            raise ComponentLookupError, \
                  "No Content Component Definition named '%s' found" %type_name

        self.definition = matching[0]
        self.schema = self.definition.schema
        self.label = 'Add %s' %self.definition.name
        super(AddContentComponentInstanceView, self).__init__(self.context,
                                                              request)
        return self.generated_form

    def createAndAdd(self, data):
        """Create a Content Component Instance and add it to the container."""
        schema = self.definition.schema
        if self.definition.copySchema:
            schema = copy.deepcopy(schema)
        content = ContentComponentInstance(self.definition.name,
                                           schema,
                                           self.definition.permissions)
        errors = []
        for name, value in data.items():
            field = self.schema[name]
            try:
                field.set(content, data[name])
            except ValidationError:
                errors.append(sys.exc_info()[1])

        content = self.add(content)

        if errors:
            raise WidgetsError(*errors)

        return content


class EditContentComponentInstanceView(EditView):

    def __init__(self, context, request):
        self.schema = context.getSchema()
        self.label = 'Edit %s' %context.__name__
        super(EditContentComponentInstanceView, self).__init__(context,
                                                               request)

