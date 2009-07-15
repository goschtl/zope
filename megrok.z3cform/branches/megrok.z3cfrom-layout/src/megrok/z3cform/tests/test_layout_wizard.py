"""
megrok layout wizard
====================

basic setup
-----------

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()

  >>> from zope import component
  >>> from zope.interface import alsoProvides
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest() 
  >>> alsoProvides(request, FormWizardPage)

  >>> christian = Person()
  >>> root['christian'] = christian
  >>> christian.__parent__ = root
  >>> christian.__name__ = u'christian'

  >>> from zope.component import getMultiAdapter
  >>> pw = getMultiAdapter((christian, request), name=u"personwizardpage")
  >>> pw
  <PersonWizardPage 'personwizardpage'>  

  >>> obj, names = pw.browserDefault(request)
  >>> obj
  <PersonWizardPage 'personwizardpage'>  

  >>> names
  ('personstepp',)

Render the personStep
---------------------

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
            <a href="http://127.0.0.1/christian/personwizardpage/addressstepp">Address</a>
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

Call the PersonStep
-------------------

  >>> print personStep()
  <html>
   <body>
     <div class="layout"><div class="wizard">
      <div class="header">Person Wizard</div>
      <div class="wizardMenu">
        <span class="selected">
            <span>Person</span>
        </span>
        <span>
            <a href="http://127.0.0.1/christian/personwizardpage/addressstepp">Address</a>
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
  </div>
   </body>
  </html>

"""

import grok
import zope.schema
import zope.interface
import megrok.layout

from megrok import z3cform
from z3c.wizard import wizard, step
from zope.location.interfaces import ILocation
from zope.schema.fieldproperty import FieldProperty


class FormWizardPage(z3cform.FormLayer):
    grok.skin('formwizardpage')


grok.layer(FormWizardPage)


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


class Layout(megrok.layout.Layout):
    grok.context(Person)


class IPersonWizard(z3cform.IWizard):
    """Person wizard marker."""

class PersonWizardPage(z3cform.WizardForm):
    """ Wizard form."""
    grok.implements(IPersonWizard)
    grok.context(Person)

    label = u'Person Wizard'

    def setUpSteps(self):
        return [
            step.addStep(self, 'personstepp', weight=1),
            step.addStep(self, 'addressstepp', weight=2),
            ]


class PersonStepP(z3cform.LayoutStep):
    grok.context(PersonWizardPage)
    label = u'Person'
    fields = z3cform.field.Fields(IPerson).select('firstName', 'lastName')


class AddressStepP(z3cform.LayoutStep):
    grok.context(PersonWizardPage)
    label = u'Address'
    fields = z3cform.field.Fields(IPerson).select('street', 'city')


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

