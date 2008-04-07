##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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

$Id$
"""
from zope import schema, interface, component
from zope.component import getAdapters, getUtility, queryMultiAdapter

from zope.app.form.utility import setUpWidget
from zope.app.form.interfaces import IInputWidget

from zope.publisher.interfaces import NotFound
from zope.app.security.vocabulary import PrincipalSource
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from z3ext.preferences.interfaces import IPreferenceGroup
from z3ext.statusmessage.interfaces import IStatusMessage

from z3ext.principals.i18n import _
from z3ext.principals.interfaces import IPrincipalFactory
from z3ext.principals.interfaces import IPrincipalPreferences
from z3ext.principals.interfaces import IPrincipalsManagement


class ManagementView(object):
    interface.implements(IPrincipalsManagement)

    label = _('Select principal')

    def factories(self):
        factories = []
        for name, factory in getAdapters(
            (self.context, self.request), IPrincipalFactory):
            factories.append((factory.title, name, factory))

        factories.sort()
        return [factory for t,n,factory in factories]

    def setupWidgets(self):
        self.principal = schema.Choice(
            title = _(u"Principal"),
            description = _(u"Select principal to view/edit."),
            source = PrincipalSource(),
            required = False)

        setUpWidget(self, 'principal', self.principal, IInputWidget)
        self.widgets = {'principal': self.principal_widget}

    def update(self):
        request = self.request

        self.setupWidgets()

        if 'form.view' in request:
            principal = self.principal_widget.getInputValue()
            if not principal:
                IStatusMessage(request).add(
                    _(u'Please select principal.'), 'warning')
            else:
                self.redirect('%s/@@index.html'%principal)


class TraverserPlugin(object):
    component.adapts(IPrincipalsManagement, interface.Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        context = self.context

        view = queryMultiAdapter((context, request), name=name)
        if view is not None:
            return view

        try:
            principal = getUtility(IAuthentication).getPrincipal(name)
        except PrincipalLookupError:
            raise NotFound(context, name, request)

        root = getUtility(IPreferenceGroup)
        root = root.__bind__(context, principal)
        root.__name__ = name

        interface.alsoProvides(root, IPrincipalPreferences)
        return root
