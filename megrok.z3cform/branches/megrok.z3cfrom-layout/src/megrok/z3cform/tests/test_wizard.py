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
  >>> alsoProvides(request, FormWizardLayer)

  >>> person = Person()
  >>> root['person'] = person
  >>> person.__parent__ = root
  >>> person.__name__ = u'person'

  >>> from zope.component import getMultiAdapter
  >>> pw = getMultiAdapter((person, request), name=u"personwizard")
  >>> pw
  <PersonWizard 'personwizard'>

  >>> obj, names = pw.browserDefault(request)
  >>> obj
  <PersonWizard 'personwizard'>

  >>> names
  ('personstep',)

Render the personStep

  >>> personStep = obj.publishTraverse(request, names[0])
  >>> personStep.update()
  >>> page = personStep.render()
  >>> print page
  <div class="wizard">
      <div class="header">Person Wizard</div>
      <div class="wizardMenu">
        <span class="selected">
            <span>Person</span>
        </span>
        <span>
            <a href="http://127.0.0.1/person/personwizard/addressstep">Address</a>
        </span>
      </div>
    <form action="http://127.0.0.1" method="post"
          enctype="multipart/form-data" class="edit-form"
          id="form">
        <div class="viewspace">
            <div class="label">Person</div>
            <div class="required-info">
               <span class="required">*</span>
               &ndash; required
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
    </form>
  </div>

Sending an request but with no data

  >>> request = TestRequest(form={'form.buttons.next': 'Next'})
  >>> alsoProvides(request, FormWizardLayer)
  >>> personWizard = PersonWizard(person, request)
  >>> personWizard.__parent__ = person
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
  >>> alsoProvides(request, FormWizardLayer)
  >>> personWizard = PersonWizard(person, request)
  >>> personWizard.__parent__ = person
  >>> personWizard.__name__ = u'wizard'
  >>> personStep = personWizard.publishTraverse(request, names[0])
  >>> personStep.update()
  >>> print personStep.render()

  >>> print personWizard.nextURL
  http://127.0.0.1/person/wizard/addressstep

"""

import grok
import zope.schema
import zope.interface

from megrok import z3cform
from z3c.wizard import wizard, step
from zope.location.interfaces import ILocation
from zope.schema.fieldproperty import FieldProperty


class FormWizardLayer(z3cform.FormLayer):
    grok.skin('formwizardlayer')


grok.layer(FormWizardLayer)


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


class IPersonWizard(z3cform.IWizard):
    """Person wizard marker."""

class PersonWizard(z3cform.WizardForm):
    """ Wizard form."""
    grok.implements(IPersonWizard)
    grok.context(Person)

    label = u'Person Wizard'

    def setUpSteps(self):
        return [
            step.addStep(self, 'personstep', weight=1),
            step.addStep(self, 'addressstep', weight=2),
            ]


class PersonStep(z3cform.Step):
    grok.context(PersonWizard)
    label = u'Person'
    fields = z3cform.field.Fields(IPerson).select('firstName', 'lastName')


class AddressStep(z3cform.Step):
    grok.context(PersonWizard)
    label = u'Address'
    fields = z3cform.field.Fields(IPerson).select('street', 'city')


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

