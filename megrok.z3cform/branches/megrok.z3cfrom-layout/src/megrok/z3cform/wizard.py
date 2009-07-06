import martian
import grokcore.view

from z3c.wizard import wizard, step
from megrok.z3cform.components import GrokForm
from z3c.form import form 

class WizardForm(GrokForm, wizard.Wizard, grokcore.view.View):
    """Base Class for a z3cwizdard.
    """
    martian.baseclass()

    def update(self):
	self.updateForm()


class Step(step.EditStep):
    """A Step for the Witzard
    """
