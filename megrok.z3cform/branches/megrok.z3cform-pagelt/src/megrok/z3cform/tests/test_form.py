"""
  >>> from zope.app.testing.functional import getRootFolder
  >>> manfred = Mammoth()
  >>> getRootFolder()["manfred"] = manfred 
  >>> import interlude

  >>> from zope import component
  >>> from zope.interface import alsoProvides
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> alsoProvides(request, FormSkin)

  Check that fields have been created on the edition page:

  >>> view = component.getMultiAdapter((manfred, request), name='edit')
  >>> view
  <megrok.z3cform.tests.test_form.Edit object at ...>

  If we call the EditPage we found it in the renderd Layout
  
  >>> '<div class="layout">' in view()
  True

  If we call the render method we get the edit-page without the layout

  >>> print view.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="form" id="form">
    <div class="viewspace">
        <div class="required-info">
           <span class="required">*</span>
           &ndash; required
        </div>
      <div>
            <div id="form-widgets-name-row" class="row">
                <div class="label">
                  <label for="form-widgets-name">
                    <span>Name</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget"><input type="text" id="form-widgets-name"
         name="form.widgets.name"
         class="text-widget required textline-field" value="" />
  </div>
            </div>
            <div id="form-widgets-age-row" class="row">
                <div class="label">
                  <label for="form-widgets-age">
                    <span>Age</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget"><input type="text" id="form-widgets-age"
         name="form.widgets.age"
         class="text-widget required int-field" value="" />
  </div>
            </div>
      </div>
    </div>
    <div>
      <div class="buttons">
        <input type="submit" id="form-buttons-apply"
         name="form.buttons.apply"
         class="submit-widget button-field" value="Apply" />
      </div>
    </div>
  </form>

Does the handy url function works

  >>> view.url()
  'http://127.0.0.1/manfred/edit'

We set in the update method of our EditForm the property updateMaker
to true. 

  >>> view.updateMarker
  True

"""

import grok
import megrok.pagelet

from megrok import z3cform
from zope import interface, schema
from zope.schema.fieldproperty import FieldProperty

from z3c.form import button, field

class FormSkin(z3cform.FormLayer):
    grok.skin('formskin')

grok.layer(FormSkin)



class IMammoth(interface.Interface):
    name = schema.TextLine(title=u"Name")
    age = schema.Int(title=u"Age")

class Mammoth(grok.Model):
    interface.implements(IMammoth)

    name = FieldProperty(IMammoth['name'])
    age = FieldProperty(IMammoth['age'])


class MyLayout(megrok.pagelet.Layout):
    grok.context(Mammoth)
    megrok.pagelet.template('templates/layout.pt')

class Edit(z3cform.EditForm):
    fields = field.Fields(IMammoth)

    def update(self):
	self.updateMarker = True


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite 
