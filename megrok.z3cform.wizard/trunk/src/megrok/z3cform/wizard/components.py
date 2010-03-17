import martian
import grokcore.view
import megrok.layout

from z3c.form import form
from zope import component
from z3c.wizard import wizard, step
from megrok.z3cform.base import PageForm, Form
from zope.publisher.publish import mapply
from megrok.layout import Page

class WizardForm(Form, wizard.Wizard, grokcore.view.View):
    """Base Class for a z3c.wizdard.
    """
    martian.baseclass()

    def update(self):
        self.updateForm()

class BaseStep(step.EditStep):
    """ Base Step
    """

class Step(BaseStep):
    """A Step for the Witzard
    """
    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return
        return self.render()


class PageStep(Page, BaseStep):
    """A Step for the Witzard
    """
   
    def __init__(self, context, request, wizard):
        self.context = context
        self.request = request
        self.wizard = self.__parent__ = wizard

    def update(self):
        BaseStep.update(self)

    def render(self):
        return BaseStep.render(self)
