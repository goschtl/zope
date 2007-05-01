##############################################################################
#
# Copyright (c) 2003 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Sharing view


$Id$
"""
import datetime

from zc.sharing import interfaces
from zc.table import table, column
import zc.table.interfaces
from zope import schema, component, interface
from zope.app import zapi
from zope.location.interfaces import ISublocations
from zope.interface import Interface
from zope.interface.common.idatetime import ITZInfo
from zope.security.interfaces import IGroup
import zope.app.security.interfaces

from zc.sharing.i18n import _
from zc.security.interfaces import ISimpleGroupSearch
from zc.security.interfaces import ISimpleUserSearch
from zc.sharing import policy
from zc.sharing.sharing import sharingMask, getPrivilege

class IPrivilegeColumn(interface.Interface):
    """Marker interface for internal use."""

class PrincipalColumn(column.SortingColumn):    
    # we don't want a sorting header, just the convenience of sorting,
    # so remove the declaration of sortable headers (XXX is this really
    # what we want)
    interface.implementsOnly(zc.table.interfaces.IColumn)

    def renderCell(self, item, formatter):
        principal_id, setting = item
        principals = zapi.principals()
        principal = principals.getPrincipal(principal_id)
        if IGroup.providedBy(principal):
            icon = 'group_icon.gif'
        else:
            icon = 'user_icon.gif'
        resource = component.getAdapter(formatter.request, Interface,
                                        icon)
        return '<img src="%s"> %s' % (resource(), principal.title)

    def getSortKey(self, item, formatter):
        principal_id, setting = item
        principals = zapi.principals()
        principal = principals.getPrincipal(principal_id)
        return principal.title.lower()


def _getgetbit(sharing, bit):
    v = 2**bit
    def getbit(data):
        return bool(sharing.getBinaryPrivileges(data[0]) & v)
    return getbit

def _getsetbit(sharing, bit):
    mask = 1 << bit
    def setbit(data, v):
        v = bool(v) << bit
        current = sharing.getBinaryPrivileges(data[0])
        result = ((current | mask) ^ mask) | v
        sharing.setBinaryPrivileges(data[0], result)
    return setbit

def _privilegeColumn(priv, sharing):
    col = column.FieldEditColumn(
        priv['title'], "sharing",
        schema.Bool(__name__=str(priv['id'])),
        lambda data: data[0],
        getter = _getgetbit(sharing, priv['id']),
        setter = _getsetbit(sharing, priv['id']),
        )
    interface.alsoProvides(col, IPrivilegeColumn)
    return col



class SharingTab:
    # This view has some weird implementation details due to the
    # dynamic computation of the items passed to the table formatter.
    #
    # The table formatter is created twice; the first time to read
    # input from the table using the initial set of items, and the
    # second time with the final set of items; only the latter is used
    # for rendering.
    #
    # Future changes to the table formatter API may make it possible
    # for this view to be less weird.

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.sharing = sharing = interfaces.IBaseSharing(self.context)

        privids = interfaces.ISharingPrivileges(self.context).privileges
        privs = [getPrivilege(id) for id in privids]
        self.nPrivileges = len(privs)

        columns = [_privilegeColumn(priv, sharing) for priv in privs]

        sprivids = interfaces.ISubobjectSharingPrivileges(self.context, None)
        if sprivids is not None:
            sprivids = [id for id in sprivids.subobjectPrivileges
                        if id not in privids]
            if sprivids:
                sprivs = [getPrivilege(id) for id in sprivids]
                columns.extend([_privilegeColumn(priv, sharing)
                                for priv in sprivs])
            self.nSubobjectPrivileges = len(sprivids)
        else:
            self.nSubobjectPrivileges = 0

        self.columns = [
            column.SubmitColumn(
                "",
                prefix="remove",
                idgetter=lambda data: str(data[0]),
                action=lambda d: self.sharing.setBinaryPrivileges(
                    d[0], 0),
                labelgetter=lambda data, formatter: _('Remove'),
                condition=lambda d: d[0] in self.sharing.getPrincipals()
                ),
            PrincipalColumn(_("Name"))] + columns

        self.factory = component.getUtility(
            zc.table.interfaces.IFormatterFactory)

        self.processInput()

        self.formatter = self.factory(
            context, request, self.settings, columns=self.columns, 
            sort_on=[('Name', False)])

    def processInput(self):
        request = self.request
        sharing = self.sharing

        # XXX completely untested, afaik; we should also set up an i18n domain
        # and provide a facility on the view for 'translating' the names for
        # labels.
        macro_name = request.form.get('apply_sharing_macro')
        if macro_name:
            macro = component.getAdapter(
                self.context, interfaces.ISharingMacro,
                macro_name)
            macro.share(sharing)

        updated = False
        form = request.form
        settings = []
        effective_principal_text = form.get('effective_principal_text', '')
        effective_principal_type = form.get('effective_principal_type', '')
        principal_text = form.get('principal_text', '')
        principal_type = form.get('principal_type', '')
        if 'principal_search' in form:
            effective_principal_text = principal_text
            effective_principal_type = principal_type
        self.effective_principal_text = effective_principal_text
        self.effective_principal_type = effective_principal_type
        self.principal_text = principal_text
        self.principal_type = principal_type

        settingsFactory = lambda: []

        if effective_principal_type=='group':
            searcher = ISimpleGroupSearch(zapi.principals(), None)
            # TODO the absence of a searcher should be logged as an error
            if searcher is not None:
                res = [[pid, 0]
                       for pid in searcher.searchGroups(
                        effective_principal_text, 0, 999999999)]
                settingsFactory = lambda: res
        elif effective_principal_type=='user' and effective_principal_text:
            searcher = ISimpleUserSearch(zapi.principals(), None)
            # TODO the absence of a searcher should be logged as an error
            if searcher is not None:
                res = [[pid, 0]
                       for pid in searcher.searchUsers(
                        effective_principal_text, 0, 999999999)]
                settingsFactory = lambda: res
        else:
            if effective_principal_type=='user':
                self.message = _('You must supply search text to find a user')
            def settingsFactory():
                return [[pid, sharing.getBinaryPrivileges(pid)]
                        for pid in sharing.getPrincipals()]

        settings = settingsFactory()
        input = self.columns[0].input(settings, request)
        if input:
            self.columns[0].update(settings, input) # inefficient :-(
            settings = settingsFactory()

        if 'setSharingInfo' in request or 'setRecursiveSharingInfo' in request:
            # apply button
            for column in self.columns:
                if not IPrivilegeColumn.providedBy(column):
                    continue
                input = column.input(settings, request)
                if input:
                    updated = column.update(settings, input) or updated

            # Reset settings, since we always show existing settings
            # after an update
            settings = [[pid, sharing.getBinaryPrivileges(pid)]
                        for pid in sharing.getPrincipals()]
            self.effective_principal_text = ''
            self.effective_principal_type = ''

            if 'setRecursiveSharingInfo' in request:
                applyToSubobjects(settings, self.context, {})
                updated = True # we'll guess :-/

        self.settings = settings
        self.updated = updated

    def subobjects(self):
        subs = ISublocations(self.context, None)
        if subs is None:
            return False
        subs = iter(subs.sublocations())
        try:
            subs.next()
        except StopIteration:
            return False
        return True

    def macros(self):
        macros = [
            (macro.order, name, macro)
            for (name, macro)
            in component.getAdapters((self.context,), interfaces.ISharingMacro)
            ]
        macros.sort()
        return [name for (order, name, macro) in macros]

    @property
    def message(self):
        if self.updated:
            formatter = self.request.locale.dates.getFormatter('dateTime', 
                                                               'medium')
            status = _("Updated on ${date_time}", 
                       mapping={'date_time': formatter.format(
                        datetime.datetime.now(ITZInfo(self.request, None)))})
            
            return status
        else:
            return ''

    def newTableFormatter(self, settings, columns=None):
        if columns is None:
            columns = self.columns
        return self.factory(
            self.context, self.request, settings, columns=columns,
            sort_on=[('Name', False)])

def applyToSubobjects(settings, ob, seen):
    obid = id(ob)
    if obid in seen:
        return
    seen[obid] = ob

    sharing = interfaces.IBaseSharing(ob, None)
    if sharing is not None:
        mask = sharingMask(ob)
        for principal in sharing.getPrincipals():
            sharing.setBinaryPrivileges(principal, 0)
        for principal, setting in settings:
            sharing.setBinaryPrivileges(principal, setting & mask)

    subs = ISublocations(ob, None)
    if subs is None:
        return

    for sub in subs.sublocations():
        applyToSubobjects(settings, sub, seen)
