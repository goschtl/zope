##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Content Component Views

$Id: content.py,v 1.2 2003/08/16 00:43:11 srichter Exp $
"""
from zope.app import zapi
from zope.app.browser.form.add import AddView
from zope.app.browser.form.editview import EditView
from zope.app.browser.form.submit import Update
from zope.app.form.utility import setUpWidget
from zope.app.interfaces.utilities.content import IContentComponentDefinition
from zope.app.security.permission import PermissionField
from zope.app.services.servicenames import Utilities
from zope.app.utilities.content import ContentComponentInstance
from zope.component.exceptions import ComponentLookupError
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.schema import getFieldNamesInOrder, getFieldsInOrder
from zope.security.checker import CheckerPublic
from zope.security.proxy import trustedRemoveSecurityProxy

class ContentComponentPermissionEdit(EditView):

    def __init__(self, context, request):
        super(ContentComponentPermissionEdit, self).__init__(context, request)
        self.buildPermissionWidgets()

    def buildPermissionWidgets(self):
        schema = self.context.schema
        for name, field in getFieldsInOrder(schema):
            # Try to get current settings
            if self.context.permissions.has_key(name):
                get_perm, set_perm = self.context.permissions[name]
            else:
                get_perm, set_perm = None, None

            # Create the Accessor Permission Widget for this field
            permField = PermissionField(
                __name__=name+'_get_perm',
                title=u"Accessor Permission",
                default=CheckerPublic,
                required=False)
            setUpWidget(self, name+'_get_perm', permField, value=get_perm)

            # Create the Mutator Permission Widget for this field
            permField = PermissionField(
                __name__=name+'_set_perm',
                title=u"Mutator Permission",
                default=CheckerPublic,
                required=False)
            setUpWidget(self, name+'_set_perm', permField, value=set_perm)

    def update(self):
        status = ''

        if Update in self.request:
            status = super(ContentComponentPermissionEdit, self).update()
            self.buildPermissionWidgets()
        elif 'CHANGE' in self.request:
            schema = self.context.schema
            perms = trustedRemoveSecurityProxy(self.context.permissions)
            for name, field in getFieldsInOrder(schema):
                getPerm = getattr(self, name+'_get_perm_widget').getData()
                setPerm = getattr(self, name+'_set_perm_widget').getData()
                perms[name] = (getPerm, setPerm)
            status = 'Fields permissions mapping updated.'

        return status

    def getPermissionWidgets(self):
        schema = self.context.schema
        info = []
        for name, field in getFieldsInOrder(schema):
            field = trustedRemoveSecurityProxy(field)
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
        """See zope.app.interfaces.container.IAdding"""
        if '=' in name:
            type_name, content_name = name.split("=", 1)
            self.context.contentName = content_name

        utilities = zapi.getService(self.context, Utilities)
        matching = utilities.getRegisteredMatching(IContentComponentDefinition,
                                                   type_name)
        if not (matching and matching[0][2].active()):
            raise ComponentLookupError, \
                  "No Content Component Definition named '%s' found" %type_name

        self.definition = matching[0][2].active().getComponent()
        self.schema = self.definition.schema
        self.label = 'Add %s' %self.definition.name
        super(AddContentComponentInstanceView, self).__init__(self.context,
                                                              request)

        return self.generated_form

    def createAndAdd(self, data):
        """Create a Content Component Instance and add it to the container."""
        content = ContentComponentInstance(self.definition.name,
                                           self.definition.schema,
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


