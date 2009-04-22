"""
  >>> from zope.app.testing.functional import getRootFolder
  >>> manfred = Person()
  >>> getRootFolder()["person"] = manfred
  >>> import interlude

  >>> from zope import component
  >>> from zope.interface import alsoProvides
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> alsoProvides(request, WizardSkin)

  Check that fields have been created on the edition page:

  >>> view = component.getMultiAdapter((manfred, request), name='personwizard')
  >>> view
  <PersonWizard 'personwizard'>

  >>> view.steps
  [<PersonStep 'person'>, <AdressStep 'address'>]

  >>> wiz = PersonWizard(manfred,request)
  >>> wiz.__name__ = u'wizard'

  >>> obj, names = wiz.browserDefault(request)
  >>> obj
  <PersonWizard 'personwizard'> 
  >>> names
  ('person',)

  >>> personStep = obj.publishTraverse(request, names[0])
  >>> personStep.update()
  >>> print personStep.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        id="form">
  <BLANKLINE>
    <div class="viewspace">
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
        <div class="required-info">
           <span class="required">*</span>
           &ndash; required
        </div>
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
      <div>
  <BLANKLINE>
  <BLANKLINE>
            <div id="form-widgets-street-row" class="row">
  <BLANKLINE>
                <div class="label">
                  <label for="form-widgets-street">
                    <span>Street</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget"><input type="text" id="form-widgets-street"
         name="form.widgets.street"
         class="text-widget required textline-field" value="" />
  </div>
  <BLANKLINE>
  <BLANKLINE>
            </div>
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
            <div id="form-widgets-city-row" class="row">
  <BLANKLINE>
                <div class="label">
                  <label for="form-widgets-city">
                    <span>City</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget"><input type="text" id="form-widgets-city"
         name="form.widgets.city"
         class="text-widget required textline-field" value="" />
  </div>
  <BLANKLINE>
  <BLANKLINE>
            </div>
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
      </div>
  <BLANKLINE>
  <BLANKLINE>
    </div>
  <BLANKLINE>
    <div>
      <div class="buttons">
        <input type="submit" id="form-buttons-apply"
         name="form.buttons.apply"
         class="submit-widget button-field" value="Apply" />
  <BLANKLINE>
      </div>
    </div>
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
  <BLANKLINE>
  </form>
  <BLANKLINE>


"""

import grok
import megrok.pagelet

from megrok import z3cform
from zope import interface, schema
from zope.schema.fieldproperty import FieldProperty

from z3c.form import button, field

class WizardSkin(z3cform.FormLayer):
    grok.skin('wizardskin')

grok.layer(WizardSkin)


class IPerson(interface.Interface):
    firstName = schema.TextLine(title=u'First Name')
    lastName = schema.TextLine(title=u'Last Name')
    street = schema.TextLine(title=u'Street')
    city = schema.TextLine(title=u'City')


class Person(grok.Model):
    interface.implements(IPerson)

    firstName = FieldProperty(IPerson['firstName'])
    lastName = FieldProperty(IPerson['lastName'])
    street = FieldProperty(IPerson['street'])
    city = FieldProperty(IPerson['city'])


class MyLayout(megrok.pagelet.Layout):
    grok.context(Person)
    megrok.pagelet.template('templates/layout.pt')

class PersonWizard(z3cform.WizardForm):
    grok.context(Person)
    fields = field.Fields(IPerson)
    label = u'Person Wizard'

    def setUpSteps(self):
        return [
                z3cform.step.addStep(self, 'person', weight=1),
                z3cform.step.addStep(self, 'address', weight=2),
                ]

from zope.publisher.interfaces.http import IHTTPRequest
class AdressStep(z3cform.Step):
    grok.name('address')
    grok.adapts(Person, IHTTPRequest, PersonWizard)
    grok.context(PersonWizard)
    fields = field.Fields(IPerson).select('firstName', 'lastName')

class PersonStep(z3cform.Step):
    grok.name('person')
    grok.adapts(Person, IHTTPRequest, PersonWizard)
    grok.context(PersonWizard)
    fields = field.Fields(IPerson).select('street', 'city')


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite 
