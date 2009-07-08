import martian
import grokcore.view

from z3c.form import form 
from z3c.wizard import wizard, step
from zope.publisher.publish import mapply
from megrok.z3cform.components import GrokForm

class WizardForm(GrokForm, wizard.Wizard, grokcore.view.View):
    """Base Class for a z3cwizdard.
    """
    martian.baseclass()

    def update(self):
	self.updateForm()


class Step(step.EditStep):
    """A Step for the Witzard
    """
    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return
        return self.render()
   
