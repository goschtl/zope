##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Content Component Definition/Instance Views

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
from zope.security import proxy, checker
from zope.formlib import form
from zope.app import apidoc
from zope.app import zapi
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.form import utility
from zope.app.form.interfaces import IInputWidget

from zope.webdev import interfaces, content
from zope.webdev.interfaces import _
from zope.webdev.browser import base, package

class AddForm(base.UtilityAddFormBase):

    label = _('Content Component Definition')

    form_fields = form.Fields(interfaces.IContentComponentDefinition).select(
        'name', 'schema')

    interface = interfaces.IContentComponentDefinition

    def create(self, data):
        return content.ContentComponentDefinition(**data)


class Overview(base.EditFormBase):
    """Page Overview."""
    form_fields = form.Fields(interfaces.IContentComponentDefinition).select(
        'name', 'schema')
    template = ViewPageTemplateFile('contentdefinition_overview.pt')


class Permissions(form.FormBase):
    """Page Overview."""

    template = ViewPageTemplateFile('contentdefinition_permission.pt')

    # XXX
    def validate(self, action, data):
        pass

    def setUpWidgets(self, ignore_request=False):
        schema = proxy.removeSecurityProxy(self.context.schema)
        for name, field in zope.schema.getFieldsInOrder(schema):

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
            permField = zope.schema.Choice(
                __name__=name+'_get_perm',
                title=u"Accessor Permission",
                default=checker.CheckerPublic,
                vocabulary="Permission Ids",
                required=False)
            utility.setUpWidget(self, name+'_get_perm', permField, IInputWidget,
                        value=get_perm_id, ignoreStickyValues=True)

            # Create the Mutator Permission Widget for this field
            permField = zope.schema.Choice(
                __name__=name+'_set_perm',
                title=u"Mutator Permission",
                default=checker.CheckerPublic,
                vocabulary="Permission Ids",
                required=False)
            utility.setUpWidget(self, name+'_set_perm', permField, IInputWidget,
                        value=set_perm_id, ignoreStickyValues=True)


    def getPermissionWidgets(self):
        schema = proxy.removeSecurityProxy(self.context.schema)
        info = []
        for name, field in zope.schema.getFieldsInOrder(schema):
            field = proxy.removeSecurityProxy(field)
            info.append(
                {'fieldName': name,
                 'fieldTitle': field.title,
                 'getter': getattr(self, name+'_get_perm_widget'),
                 'setter': getattr(self, name+'_set_perm_widget')} )
        return info


    @form.action(_("Apply"))
    def handleEditAction(self, action, data):
        schema = self.context.schema
        perms = proxy.removeSecurityProxy(self.context.permissions)
        for name, field in zope.schema.getFieldsInOrder(schema):
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

        self.status = _('Fields permissions mapping updated.')


    @form.action(_("Cancel"))
    def handleCancelAction(self, action, data):
        pass


class PackageOverview(object):
    """A pagelet that serves as the overview of the content component
    definitions in the package overview."""
    zope.interface.implements(package.IPackageOverviewPagelet)

    title = _('Content Component Definitions')

    def icon(self):
        return zapi.getAdapter(self.request, name='content.png')()

    def definitions(self):
        """Return PT-friendly info dictionaries for all definitions."""
        return [
            {'name': value.name,
             'schema': apidoc.utilities.getPythonPath(value.schema),
             'url': zapi.absoluteURL(value, self.request)}
            for value in self.context.values()
            if interfaces.IContentComponentDefinition.providedBy(value)]
