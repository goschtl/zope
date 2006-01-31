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
"""Some base classes of views.

$Id$
"""
__docformat__ = "reStructuredText"
import datetime
import pytz
import zope.event

from zope.formlib import form
from zope.interface.common import idatetime
from zope.app import component
from zope.app import zapi
from zope.app.pagetemplate import ViewPageTemplateFile

from zope.webdev.interfaces import _

class UtilityAddFormBase(form.AddForm):
    """Add form for utilities."""

    # Must be provide the interface
    interface = None

    template = ViewPageTemplateFile('addform.pt')

    def add(self, object):
        object = super(UtilityAddFormBase, self).add(object)

        # Add registration
        name = zapi.getName(object)
        package = self.context.context
        registration = component.site.UtilityRegistration(
            name, self.interface, object)
        package.registrationManager.addRegistration(registration)
        registration.status = component.interfaces.registration.ActiveStatus

        return object

    def nextURL(self):
        return zapi.absoluteURL(self.context.context, self.request)


def haveEditFlag(form, action):
    if 'doEdit' in form.request:
        return True
    return False

class EditFormBase(form.EditForm):
    '''A base class for display forms that are also edit forms.'''

    form_edit_widgets = None

    def fixUpWidgets(self):
        pass

    def setUpWidgets(self, ignore_request=False):
        for_display = True
        if 'doEdit' in self.request:
            for_display = False
            if self.form_edit_widgets:
                for key, value in self.form_edit_widgets.items():
                    self.form_fields[key].custom_widget = value

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
