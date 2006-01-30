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
"""Package Browser Code.

$Id$
"""
__docformat__ = "reStructuredText"
import datetime
import pytz

import zope.event
import zope.interface
import zope.schema
import zope.app.event.objectevent
from zope import viewlet
from zope.formlib import form
from zope.interface.common import idatetime
from zope.app import zapi
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.webdev import interfaces
from zope.webdev.browser import pagelet

from zope.webdev.interfaces import _

def haveEditFlag(form, action):
    if 'doEdit' in form.request:
        return True
    return False

class Overview(form.EditForm):
    """Package Overview."""

    form_fields = form.Fields(interfaces.IPackage).select(
        'docstring', 'version', 'license', 'author')
    template = ViewPageTemplateFile('package_overview.pt')

    def fixUpWidgets(self):
        self.widgets.get('docstring').height = 3

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
        if not for_display:
            self.fixUpWidgets()

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


class IPackageOverviewManager(pagelet.IPageletManager):
    """A pagelet manager to display contents of a package."""


class IPackageOverviewPagelet(pagelet.IPagelet):
    """A pagelet that is displayed in the package overview pagelet manager."""

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'The title of the pagelet.',
        required=True)


class PackageOverviewManager(pagelet.PageletManagerBase,
                             viewlet.manager.ViewletManagerBase):
    """Ordered pagelet manager."""
    zope.interface.implements(IPackageOverviewManager)

    def sort(self, viewlets):
        """Sort the viewlets on their weight."""
        return sorted(viewlets,
                      lambda x, y: cmp(int(x[1].weight), int(y[1].weight)))
