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
$Id$
"""
__docformat__ = "reStructuredText"
from zope.session.interfaces import ISession
from z3c.form import button, field, form
from z3c.formdemo.wizard import content, interfaces, wizard
from z3c.formui import layout


infoSelection = (
    'firstName', 'lastName', 'phone', 'email', 'street', 'city', 'zip')

class PersonalInfoStep(wizard.Step):
    label = u'Personal Information'
    fields = field.Fields(interfaces.IPersonalInfo).select(
        'firstName', 'lastName', 'phone', 'email')

class AddressStep(wizard.Step):
    label = u'Address'
    fields = field.Fields(interfaces.IAddress)

class FatherStep(wizard.Step):
    label = u'Father'
    fields = field.Fields(interfaces.IPersonalInfo).select(*infoSelection)

    def getContent(self):
        return self.context.father

class MotherStep(wizard.Step):
    label = u'Mother'
    fields = field.Fields(interfaces.IPersonalInfo).select(*infoSelection)

    def getContent(self):
        return self.context.mother

class EmployerStep(wizard.Step):
    label = u'Employer'
    fields = field.Fields(interfaces.IEmployerInfo).select(
        'name', 'street', 'city', 'zip')

    def getContent(self):
        return self.context.employer


class PersonWizard(wizard.Wizard):
    form.extends(wizard.Wizard)

    title = u'Wizard Demo - Person Demographics'
    sessionKey = 'z3c.formdemo.wizard.person'

    steps = [
        ('personalInfo', PersonalInfoStep),
        ('address', AddressStep),
        ('father', FatherStep),
        ('mother', MotherStep),
        ('employer', EmployerStep)]

    def finish(self):
        self.request.response.redirect('summary.html')

    def getContent(self):
        session = ISession(self.request)[self.sessionKey]
        obj = session.get('content')
        if obj is None:
            obj = session['content'] = content.Person()
        return obj

    @button.buttonAndHandler(
        u'Clear', condition=lambda form: form.isFirstStep(),
        provides=(interfaces.IBackButton,))
    def handleClear(self, action):
        session = ISession(self.request)[self.sessionKey]
        del session['content']
        self.request.response.redirect(
            self.request.getURL() + '?step=' + self.steps[0][0])


class PersonSummary(layout.FormLayoutSupport, form.DisplayForm):

    fields = field.Fields(interfaces.IPersonalInfo).select(*infoSelection)

    def getContent(self):
        session = ISession(self.request)[PersonWizard.sessionKey]
        return session.get('content')

    def update(self):
        content = self.getContent()
        self.father = form.DisplayForm(content.father, self.request)
        self.father.fields = field.Fields(interfaces.IPersonalInfo).select(
            *infoSelection)
        self.father.update()

        self.mother = form.DisplayForm(content.mother, self.request)
        self.mother.fields = field.Fields(interfaces.IPersonalInfo).select(
            *infoSelection)
        self.mother.update()

        self.employer = form.DisplayForm(content.employer, self.request)
        self.employer.fields = field.Fields(interfaces.IEmployerInfo).select(
            'name', 'street', 'city', 'zip')
        self.employer.update()

        super(PersonSummary, self).update()
