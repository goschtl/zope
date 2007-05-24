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
"""Generic Wizard Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.app.session.interfaces import ISession
from zope.viewlet.viewlet import CSSViewlet

from z3c.form import button, field, form, subform
from z3c.form.interfaces import IWidgets
from z3c.formui import layout
from z3c.formdemo.wizard import interfaces

WizardCSSViewlet = CSSViewlet('wizard.css')

class IWizardButtons(zope.interface.Interface):

    previous = button.Button(
        title=u'Previous',
        condition=lambda form: not form.isFirstStep())
    zope.interface.alsoProvides(
        previous, (interfaces.ISaveButton, interfaces.IBackButton))

    save = button.Button(
        title=u'Save')
    zope.interface.alsoProvides(
        save, (interfaces.ISaveButton, interfaces.IForwardButton))

    next = button.Button(
        title=u'Next',
        condition=lambda form: not form.isLastStep())
    zope.interface.alsoProvides(
        next, (interfaces.ISaveButton, interfaces.IForwardButton))

    finish = button.Button(
        title=u'Finish',
        condition=lambda form: form.isLastStep())
    zope.interface.alsoProvides(
        finish, (interfaces.ISaveButton, interfaces.IForwardButton))


class Step(subform.EditSubForm):
    zope.interface.implements(interfaces.IStep)
    name = None
    label = None

    @button.handler(interfaces.ISaveButton)
    def handleAllButtons(self, action):
        self.handleApply(self, action)


class WizardButtonActions(button.ButtonActions):

    @property
    def backActions(self):
        return [action for action in self.values()
                if interfaces.IBackButton.providedBy(action.field)]

    @property
    def forwardActions(self):
        return [action for action in self.values()
                if interfaces.IForwardButton.providedBy(action.field)]


class Wizard(layout.FormLayoutSupport, form.Form):

    sessionKey = 'z3c.formdemo.wizard'
    buttons = button.Buttons(IWizardButtons)

    title = u'Wizard'
    steps = None
    step = None

    def getCurrentStep(self):
        session = ISession(self.request)[self.sessionKey]
        if 'step' in self.request:
            name = self.request['step']
            step = name, dict(self.steps).get(name)
        else:
            step = session.get('step', self.steps[0])
        session['step'] = step
        name, klass = step
        inst = klass(self.getContent(), self.request, self)
        inst.name = name
        return inst

    def isFirstStep(self):
        return isinstance(self.step, self.steps[0][1])

    def isLastStep(self):
        return isinstance(self.step, self.steps[-1][1])

    @property
    def stepsInfo(self):
        info = []
        for pos, (name, step) in enumerate(self.steps):
            info.append({
                'name': name,
                'number': str(pos+1),
                'active': isinstance(self.step, step),
                'class': isinstance(self.step, step) and 'active' or 'inactive'
                })
        return info

    def updateActions(self):
        self.actions = WizardButtonActions(self, self.request, self.context)
        self.actions.update()

    def update(self):
        self.step = self.getCurrentStep()
        self.updateActions()
        self.step.update()
        self.actions.execute()

    def finish(self):
        return NotImplementedError

    @button.handler(IWizardButtons['previous'])
    def handlePrevious(self, action):
        if self.step.widgets.errors:
            return
        for pos, (name, step) in enumerate(self.steps):
            if self.step.name == name:
                break
        url = self.request.getURL() + '?step=' + self.steps[pos-1][0]
        self.request.response.redirect(url)


    @button.handler(IWizardButtons['next'])
    def handleNext(self, action):
        if self.step.widgets.errors:
            return
        for pos, (name, step) in enumerate(self.steps):
            if self.step.name == name:
                break
        url = self.request.getURL() + '?step=' + self.steps[pos+1][0]
        self.request.response.redirect(url)


    @button.handler(IWizardButtons['finish'])
    def handleFinish(self, action):
        session = ISession(self.request)[self.sessionKey]
        del session['step']
        self.finish()
