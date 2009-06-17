"""
  >>> from zope.app.testing.functional import getRootFolder
  >>> manfred = Mammoth()
  >>> getRootFolder()["manfred"] = manfred 

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

  >>> view.render().startswith('<form action="http://127.0.0.1"')
  True 

Does the handy url function works

  >>> view.url()
  'http://127.0.0.1/manfred/edit'

We set in the update method of our EditForm the property updateMaker
to true. 

  >>> view.updateMarker
  True

"""

import grok
import megrok.layout

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


class MyLayout(megrok.layout.Layout):
    grok.context(Mammoth)

class Edit(z3cform.PageEditForm):
    fields = field.Fields(IMammoth)

    def update(self):
        self.updateMarker = True


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
          )
    suite.layer = FunctionalLayer
    return suite 

