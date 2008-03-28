##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Basic registration views."""

import gocept.registration.interfaces
import z3c.form.button
import z3c.form.form
import z3c.formui.layout
import zope.interface
import zope.schema

from gocept.registration.i18n import _


class ISimpleRegistrationSchema(zope.interface.Interface):

    email = zope.schema.TextLine(
        title=_(u"Email address"),
        description=_(u"Please provide your email address to which a"
                      u"confirmation email will be sent to."))


class RegistrationForm(z3c.form.form.Form):
    """Allow a user to enter his data and register itself."""

    ignoreContext = True
    email_field_name = 'email'

    fields = z3c.form.field.Fields(ISimpleRegistrationSchema)

    @z3c.form.button.buttonAndHandler(_('Register'))
    def register(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        registrations = zope.component.getUtility(
            gocept.registration.interfaces.IRegistrations)
        registrations.register(data[self.email_field_name], data)


class RegistrationPageletForm(z3c.formui.layout.FormLayoutSupport,
                              RegistrationForm):
    """Allow a user to enter his data and register itself."""


class Confirmation(object):
    """Confirm a user's registration."""

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'confirmation.pt')

    error_template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'confirmation_error.pt')

    def update(self):
        registrations = zope.component.getUtility(
            gocept.registration.interfaces.IRegistrations)
        hash = self.request.form.get('hash')
        try:
            registrations.confirm(hash)
        except KeyError:
            self.template = self.error_template
