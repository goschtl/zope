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
from zope.publisher.browser import BrowserPage
from zope.publisher.browser import TestRequest
from zope.traversing.browser import absoluteURL

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
from z3c.form.interfaces import IWidgets
from z3c.form import button
from z3c.form import form
from z3c.form import field
from z3c.formui import layout
from z3c.pagelet import browser

from z3c.website.i18n import MessageFactory as _
from z3c.website import interfaces
from z3c.website.authentication import WebSiteMember


class MemberAddForm(form.AddForm):
    """Member add form."""

    label = _(u'Add Member')

    fields = field.Fields(interfaces.IWebSiteMember).select(
        'login', 'password', 'firstName', 'lastName', 'email', 'phone')

    def create(self, data):
        # Create the member
        login = data['login']
        password = data['password']
        firstName = data['firstName']
        lastName = data['lastName']
        email = data['email']
        user = WebSiteMember(login, password, firstName, lastName, email)
        user.phone = data.get('phone', u'')
        return user

    def add(self, member):
        auth = zope.component.getUtility(IAuthentication, context=self.context)
        auth['members'].add(member)
        self._finished_add = True
        return member

    def nextURL(self):
        return absoluteURL(self.context, self.request) + '/members.html'


class MemberEditForm(form.EditForm):

    label = _('Edit Member')

    fields = field.Fields(interfaces.IWebSiteMember).select(
        'login', 'password', 'firstName', 'lastName', 'email', 'phone')

    ignoreRequest = False

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreRequest = self.ignoreRequest
        self.widgets.update()


class RadioButtonColumn(column.Column):

    def renderCell(self, item, formatter):
        name = zapi.getName(item['member'])
        widget = (u'<input type="radio" class="radioWidget" '
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


def getLogin(item):
    p = item['member']
    return p.login


def getFirstName(item):
    p = item['member']
    return p.firstName


def getLastName(item):
    p = item['member']
    return p.lastName


def getEmail(item):
    p = item['member']
    return p.email


class MemberManagement(layout.FormLayoutSupport, form.Form):
    """Management of members."""

    subForm = None

    # Only the first columns
    columns = (
        RadioButtonColumn(_('Sel')),
        GetTextColumn(_('Login'), 'lastName', getLogin),
        GetTextColumn(_('First Name'), 'email', getFirstName),
        GetTextColumn(_('Last Name'), 'phone', getLastName),
        GetTextColumn(_('Email'), 'phone', getEmail),
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
        formatter.widths = [25, 150, 150, 150, 150]
        formatter.cssClasses['table'] = 'list'
        return formatter()

    @button.buttonAndHandler(u'Edit')
    def editMember(self, action):
        if self.selectedItem:
            self.subForm = MemberEditForm(self.selectedItem, self.request)
            self.subForm.ignoreRequest = True
            self.subForm.update()
        else:
            self.status = _('No member selected for editing.')

    @button.buttonAndHandler(u'Delete')
    def deleteMember(self, action):
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

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def update(self):
        if self.selectedItem:
            self.subForm = MemberEditForm(self.selectedItem, self.request)
            self.subForm.update()
        else:
            self.subForm = MemberAddForm(self.context, self.request)
        self.subForm.update()
        if self.subForm.status is not None:
            self.status = self.subForm.status
        super(MemberManagement, self).update()
