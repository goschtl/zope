"""
megrok wizard
=============

basic setup
-----------

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()

  >>> from zope import component
  >>> from zope.interface import alsoProvides
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest() 

  >>> root['person1'] = person1 = Person()
  >>> person1.__parent__ = root
  >>> person1.__name__ = u'person'

  >>> from zope.component import getMultiAdapter
  >>> pw = getMultiAdapter((person1, request), name=u"personwizardlayout")
  >>> pw
  <PersonWizardLayout 'personwizardlayout'>

  >>> obj, names = pw.browserDefault(request)
  >>> obj
  <PersonWizardLayout 'personwizardlayout'>

  >>> names
  ('person1step',)

Render the personStep

  >>> personStep = obj.publishTraverse(request, names[0])
  >>> personStep.update()
  >>> page = personStep.render()
  >>> print page
  <div class="wizard">
      <div class="header">Person Wizard</div>
      <div class="wizardMenu">
        <span class="selected">
            <span>Person1</span>
        </span>
        <span>
            <a href="http://127.0.0.1/person/personwizardlayout/address1step">Address1</a>
        </span>
      </div>
    <form action="http://127.0.0.1" method="post"
          enctype="multipart/form-data" class="edit-form"
          name="form" id="form">
        <fieldset class="main">
        <div class="viewspace">
            <div class="label">Person1</div>
            <div class="required-info">
              <span class="required">*</span>&ndash; required
            </div>
          <div class="step">
            <div id="form-widgets-firstName-row" class="row">
                <div class="label">
                  <label for="form-widgets-firstName">
                    <span>First Name</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
      <input id="form-widgets-firstName"
             name="form.widgets.firstName"
             class="text-widget required textline-field"
             value="" type="text" />
  </div>
            </div>
            <div id="form-widgets-lastName-row" class="row">
                <div class="label">
                  <label for="form-widgets-lastName">
                    <span>Last Name</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
      <input id="form-widgets-lastName"
             name="form.widgets.lastName"
             class="text-widget required textline-field"
             value="" type="text" />
  </div>
            </div>
          </div>
            <div>
              <div class="buttons">
                <span class="back">
                </span>
                <span class="step">
  <input id="form-buttons-apply" name="form.buttons.apply"
         class="submit-widget button-field" value="Apply"
         type="submit" />
                </span>
                <span class="forward">
  <input id="form-buttons-next" name="form.buttons.next"
         class="submit-widget button-field" value="Next"
         type="submit" />
                </span>
              </div>
            </div>
        </div>
        </fieldset>
    </form>
  </div>


Sending an request but with no data

  >>> request = TestRequest(form={'form.buttons.next': 'Next'})
  >>> personWizard = PersonWizardLayout(person1, request)
  >>> personWizard.__parent__ = person1
  >>> personWizard.__name__ = u'wizard'
  >>> personStep = personWizard.publishTraverse(request, names[0])
  >>> personStep.update()
  >>> print personStep.render()
  <div class="wizard">
  ...
    <div class="summary">There were some errors.</div>
  ...
    <div class="error">Required input is missing.</div>
  ...
    <div class="error">Required input is missing.</div>
  ...
  
Sending an request with a working data set...

  >>> request = TestRequest(form={'form.widgets.firstName': u'Roger',
  ...                             'form.widgets.lastName': u'Ineichen',
  ...                             'form.buttons.next': 'Next'})
  >>> personWizard = PersonWizardLayout(person1, request)
  >>> personWizard.__parent__ = person1
  >>> personWizard.__name__ = u'wizard'
  >>> personStep = personWizard.publishTraverse(request, names[0])
  >>> personStep.update()
  >>> print personStep.render()

  >>> print personWizard.nextURL
  http://127.0.0.1/person/wizard/address1step

"""

import grokcore.component as grok
import zope.schema
import zope.interface

from megrok.z3cform import wizard as z3cwizard
from z3c.wizard import wizard, step
from zope.location.interfaces import ILocation
from zope.schema.fieldproperty import FieldProperty
from z3c.form import field
from megrok.layout import Layout


class MyLayout(Layout):
    grok.context(zope.interface.Interface)

    def render(self):
        return "<html> %s </html>" % self.view.contentn()

class IPerson(ILocation):
    """Person interface."""

    firstName = zope.schema.TextLine(title=u'First Name')
    lastName = zope.schema.TextLine(title=u'Last Name')
    street = zope.schema.TextLine(title=u'Street')
    city = zope.schema.TextLine(title=u'City')


class Person(object):
    """Person content."""
    grok.implements(IPerson)

    __name__ = __parent__ = None

    firstName = FieldProperty(IPerson['firstName'])
    lastName = FieldProperty(IPerson['lastName'])
    street = FieldProperty(IPerson['street'])
    city = FieldProperty(IPerson['city'])


class IPersonWizard(z3cwizard.IWizard):
    """Person wizard marker."""


class PersonWizardLayout(z3cwizard.WizardForm):
    """ Wizard form."""
    grok.implements(IPersonWizard)
    grok.context(Person)

    label = u'Person Wizard'

    def setUpSteps(self):
        return [
            step.addStep(self, 'person1step', weight=1),
            step.addStep(self, 'address1step', weight=2),
            ]


class Person1Step(z3cwizard.PageStep):
    grok.context(PersonWizardLayout)
    label = u'Person1'
    fields = field.Fields(IPerson).select('firstName', 'lastName')


class Address1Step(z3cwizard.PageStep):
    grok.context(PersonWizardLayout)
    label = u'Address1'
    fields = field.Fields(IPerson).select('street', 'city')


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.wizard.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

