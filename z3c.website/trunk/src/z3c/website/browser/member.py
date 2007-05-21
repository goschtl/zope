##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id: __init__.py 69382 2006-08-09 13:26:53Z rogerineichen $
"""
__docformat__ = "reStructuredText"

from email.MIMEText import MIMEText

import transaction
import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
from zope.formlib import form
from zope.publisher.browser import BrowserPage
from zope.publisher.browser import TestRequest

from zope.app import zapi
from zope.app import security
from zope.app.component import hooks
from zope.app.form.browser import TextAreaWidget
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.security.interfaces import IAuthentication
from zope.app.security import settings

from zc.table import column
from zc.table import table
from z3c.authentication.simple.interfaces import IMember
from z3c.authentication.simple.member import Member
from z3c.pagelet import browser

from z3c.website.i18n import MessageFactory as _
from z3c.website import interfaces


class AddMemberForm(form.AddFormBase):

    label = _('Add Member')
    prefix = 'memberform'
    template = ViewPageTemplateFile('member_edit.pt')
    actions = form.AddFormBase.actions.copy()

    form_fields = form.Fields(IMember).select(
        'login', 'password', 'title', 'description')

    def create(self, data):
        # Create the admin principal
        login = data['login']
        password = data['password']
        title = data['title']
        description = data['description']
        return Member(login, password, title, description)

    def add(self, member):
        auth = zope.component.getUtility(IAuthentication, context=self.context)
        auth['members'].add(member)
        self._finished_add = True
        return member

    def handle_cancel(self, action, data, errors=None):
        self.request.response.redirect(self.request.URL)

    actions.append(
        form.Action(_('Cancel'), success=handle_cancel, failure=handle_cancel))

    def nextURL(self):
        return self.request.URL


class EditMemberForm(form.EditFormBase):

    label = _('Edit Member')
    prefix = 'memberform'
    template = ViewPageTemplateFile('member_edit.pt')
    actions = form.Actions()

    form_fields = form.Fields(IMember).select(
        'login', 'password', 'title', 'description')

    @form.action(_("Apply"))
    def handle_edit_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(self.context))
            self.status = _('Member updated.')

    def handle_cancel(self, action, data, errors=None):
        self.request.response.redirect(self.request.URL)

    actions.append(
        form.Action(_('Cancel'), success=handle_cancel, failure=handle_cancel))


class RadioButtonColumn(column.Column):

    def renderCell(self, item, formatter):
        name = zapi.getName(item['member'])
        widget = (u'<input type="radio" '
                  u'name="selectedItem" value="%s" %s />')
        selected=''
        if 'selectedItem' in formatter.request and \
               formatter.request['selectedItem'] == name:
            selected='checked="checked"'
        return widget %(name, selected)


class GetTextColumn(column.Column):

    def __init__(self, title=None, name=None, getText=None):
        super(GetTextColumn, self).__init__(title, name)
        self.getText = getText

    def renderCell(self, item, formatter):
        return self.getText(item)


def getDescription(item):
    p = item['member']
    return p.description


def getTitle(item):
    p = item['member']
    return p.title


def getLogin(item):
    p = item['member']
    return p.login



class MemberManagement(browser.BrowserPagelet):
    """Management of members."""

    status = None

    label = _('Manage Members')
    prefix = 'form'
    tableActions = form.Actions()
    subForm = u''

    # Only the first columns
    columns = (
        RadioButtonColumn(_('Sel')),
        GetTextColumn(_('Login'), 'lastName', getLogin),
        GetTextColumn(_('Title'), 'email', getTitle),
        GetTextColumn(_('Description'), 'phone', getDescription),
        )

    @property
    def members(self):
        auth = zope.component.getUtility(IAuthentication)
        for name, member in auth['members'].items():
            yield {'member': member,
                   'id': name}

    @property
    def selectedItem(self):
        if not self.request.get('selectedItem'):
            return None
        auth = zope.component.getUtility(IAuthentication)
        return auth['members'][self.request['selectedItem']]

    def getEditForm(self):
        if self.subForm:
            return self.subForm.render()

    def table(self):
        # 3. Create the table formatter
        formatter = table.AlternatingRowFormatter(
            self.context, self.request, self.members, columns=self.columns,
            prefix='members.')
        formatter.widths = [25, 150, 150, 200, 200]
        formatter.cssClasses['table'] = 'sorted'
        return formatter()

    def update(self):
        if self.selectedItem:
            self.subForm = EditMemberForm(
                self.selectedItem, self.request)
        else:
            self.subForm = AddMemberForm(self.context, self.request)
        self.subForm.update()
        if self.subForm.status is not None:
            self.status = self.subForm.status

        errors, action = form.handleSubmit(
            self.tableActions, {}, lambda a, d: True)
        if action is not None:
            action.success({})

    @form.action(_('Delete Member'), tableActions)
    def deleteMember(self, action, data):
        if not self.selectedItem:
            self.status = _('No member selected.')
            return

        pid = self.request['selectedItem']
        auth = zope.component.getUtility(IAuthentication)
        del auth['members'][self.request['selectedItem']]

        # clenaup group settings for removed members
        for group in auth['groups'].values():
            if pid in group.principals:
                principals = list(group.principals)
                principals.remove(pid)
                group.setPrincipals(principals, check=False)
        self.status = _('Member has been deleted.')

    @form.action(_('Edit Member'), tableActions)
    def editMember(self, action, data):
        if self.selectedItem:
            self.subForm = EditMemberForm(self.selectedItem, self.request)
            self.subForm.resetForm()
        else:
            self.status = _('No member selected for editing.')
