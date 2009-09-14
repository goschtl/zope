import martian
import grokcore.view
import megrok.layout

from z3c.form import form
from zope import component
from z3c.wizard import wizard, step
from megrok.z3cform.base import PageForm, Form
from zope.publisher.publish import mapply

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


class LayoutStep(BaseStep):
    """A Step for the Witzard
    """

    def _render_template(self):
        assert not (self.template is None)
        if IGrokTemplate.providedBy(self.template):
            return super(Form, self)._render_template()
        return self.template(self)

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return
        if self.layout is None:
            layout = component.getMultiAdapter(
                (self.context, self.request), megrok.layout.ILayout)
            return layout(self)
        return self.layout()
