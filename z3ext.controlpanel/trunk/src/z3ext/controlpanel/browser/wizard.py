##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
from zope import interface
from zope.component import getUtility
from z3ext.layoutform import Fields, PageletEditForm
from z3ext.wizard import WizardWithTabs
from z3ext.wizard.step import WizardStep, WizardStepForm
from z3ext.wizard.button import WizardButton
from z3ext.wizard.interfaces import ISaveable, IForwardAction
from z3ext.layoutform.interfaces import ISaveAction
from z3ext.controlpanel.interfaces import _

from interfaces import IConfigletEditWizard


class ConfigletEditWizard(WizardWithTabs):
    interface.implements(IConfigletEditWizard)

    prefix = 'configlet.'
    id = 'configlet-edit-wizard'

    @property
    def title(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__


class ConfigletEditStep(WizardStepForm):
    interface.implements(ISaveable)

    name = 'configlet'
    title = _('Configure')
    label = _('Configure configlet')

    @property
    def fields(self):
        return Fields(self.getContent().__schema__)


next = WizardButton(
    title = _(u'Next'),
    condition = lambda form: not form.isLastStep() \
        and not form.step.isSaveable(),
    weight = 300,
    provides = IForwardAction)

save = WizardButton(
    title = _(u'Save'),
    condition = lambda form: form.step.isSaveable(),
    weight = 400,
    provides = ISaveAction)
