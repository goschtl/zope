import grok
import zope.schema
import zope.interface

from megrok.z3cform import wizard as z3cwizard
from z3c.wizard import wizard, step
from zope.location.interfaces import ILocation
from zope.schema.fieldproperty import FieldProperty
from z3c.form import field
from person import Person, IPerson
from grokformdemo.app import Grokformdemo


class AddWizard(grok.View):
    grok.context(Grokformdemo)

    def update(self):
        context = self.context
        self.id = "person-%s" %(str(len(context)))
        self.context[self.id] = Person()

    def render(self):
        self.redirect(self.url(self.context[self.id], 'personwizard'))


class IPersonWizard(z3cwizard.IWizard):
    """Person wizard marker."""


class PersonWizard(z3cwizard.WizardForm):
    """ Wizard form."""
    grok.implements(IPersonWizard)
    grok.context(Person)
    fields = []
    label = u'Person Wizard'

    def setUpSteps(self):
        return [
            step.addStep(self, 'personstep', weight=1),
            step.addStep(self, 'addressstep', weight=2),
            ]


class PersonStep(z3cwizard.LayoutStep):
    grok.context(PersonWizard)
    label = u'Person'
    fields = field.Fields(IPerson).select('firstName', 'lastName')


class AddressStep(z3cwizard.LayoutStep):
    grok.context(PersonWizard)
    label = u'Address'
    fields = field.Fields(IPerson).select('street', 'city')
