# -*- coding: utf-8 -*-

import martian
import grokcore.view

from z3c.wizard import wizard, step
from zope.publisher.publish import mapply
from megrok.z3cform.base import PageForm, Form


class WizardForm(Form, wizard.Wizard, grokcore.view.View):
    """Base Class for a z3c.wizdard.
    """
    martian.baseclass()

    def update(self):
        self.updateForm()


class BaseStep(step.EditStep):
    """Needed for one Grokker
    """


class Step(BaseStep):
    """A Step for the Wizard
    """

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return
        return self.render()


class PageStep(PageForm, Step):
    """A Step for the Wizard renderd in an ILayout component
    """

    def __init__(self, context, request, wizard):
        self.context = context
        self.request = request
        self.wizard = self.__parent__ = wizard

    def update(self):
        BaseStep.update(self)

    def render(self):
        return BaseStep.render(self)
