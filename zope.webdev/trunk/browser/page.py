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
"""Schema Views

$Id$
"""
__docformat__ = "reStructuredText"
import datetime
import pytz

import zope.interface
import zope.app.component.interfaces.registration
from zope.formlib import form
from zope.app import zapi
from zope.app import apidoc
from zope.webdev import interfaces, page
from zope.webdev.browser import base, package
from zope.webdev.interfaces import _
from zope.webdev.page import registerPage
from zope.security.proxy import removeSecurityProxy
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.interface.common import idatetime



def haveEditFlag(form, action):
    if 'doEdit' in form.request:
        return True
    return False


class AddForm(base.UtilityAddFormBase):

    label = _('Page')

    form_fields = form.Fields(interfaces.IPage).select(
        'name', 'for_')

    interface = interfaces.IPage

    def create(self, data):
        return page.Page(**data)

    def add(self, obj):
        obj = super(form.AddForm, self).add(obj)
        obj=removeSecurityProxy(obj)
        registerPage(obj)
        return obj


class PackageOverview(object):
    """A pagelet that serves as the overview of pages in the package
    overview."""
    zope.interface.implements(package.IPackageOverviewPagelet)

    title = _("Pages")

    def icon(self):
        return zapi.getAdapter(self.request, name='page.png')()

    def pages(self):
        """Return PT-friendly info dictionaries for all pages."""
        pages = []
        for page in self.context.values():
            if interfaces.IPage.providedBy(page):
                pages.append(
                    {'name': page.name,
                     'for':  apidoc.utilities.getPythonPath(page.for_)})

        return pages


class Overview(form.EditForm):
    """Page Overview."""

    form_fields = form.Fields(interfaces.IPage).select(
        'name', 'for_', 'layer', 'permission','templateSource',
        'moduleSource','className')
    template = ViewPageTemplateFile('package_overview.pt')

#    def fixUpWidgets(self):
#        self.widgets.get('docstring').height = 3

    def setUpWidgets(self, ignore_request=False):
        for_display = True
        if 'doEdit' in self.request:
            for_display = False

        self.adapters = {}
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, for_display=for_display,
            ignore_request=ignore_request
            )
#        if not for_display:
#            self.fixUpWidgets()

    @form.action(_("Edit"), condition=lambda *args: not haveEditFlag(*args))
    def handleStartEditAction(self, action, data):
        self.request.form['doEdit'] = True
        self.setUpWidgets()

    @form.action(_("Apply"), condition=haveEditFlag)
    def handleEditAction(self, action, data):
        del self.request.form['doEdit']

        if form.applyChanges(self.context, self.form_fields,
                             data, self.adapters):
            zope.event.notify(
                zope.app.event.objectevent.ObjectModifiedEvent(self.context))
            formatter = self.request.locale.dates.getFormatter(
                'dateTime', 'medium')

            try:
                time_zone = idatetime.ITZInfo(self.request)
            except TypeError:
                time_zone = pytz.UTC

            status = _("Updated on ${date_time}",
                       mapping={'date_time':
                                formatter.format(
                                   datetime.datetime.now(time_zone)
                                   )
                        }
                       )
            self.status = status
        else:
            self.status = _('No changes')

    @form.action(_("Cancel"), condition=haveEditFlag)
    def handleCancelAction(self, action, data):
        del self.request.form['doEdit']

