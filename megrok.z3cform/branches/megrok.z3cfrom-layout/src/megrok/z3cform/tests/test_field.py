"""
  >>> manfred = Mammoth()

  >>> from zope import component
  >>> from zope.interface import alsoProvides
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> alsoProvides(request, FormFieldSkin)

Check that fields have been created on the edition page:

  >>> view = component.getMultiAdapter((manfred, request), name='edit')
  >>> len(view.fields)
  2
  >>> [field.__name__ for field in view.fields.values()]
  ['name', 'age']

Now what happens with the render and call functions?

  >>> #view.render() 

Does the field functions (omit, select, ...) work

  >>> index = component.getMultiAdapter((manfred, request), name='index')
  >>> len(index.fields)
  1

  >>> 'name' in index.fields.keys()
  True

"""
import grok

from zope import interface, schema
from zope.schema.fieldproperty import FieldProperty
from megrok import z3cform
from z3c.form import field

class FormFieldSkin(z3cform.FormLayer):
    grok.skin('formfieldskin')

grok.layer(FormFieldSkin)



class IMammoth(interface.Interface):

    name = schema.TextLine(title=u"Name")
    age = schema.Int(title=u"Age")

class Mammoth(grok.Model):
    
    interface.implements(IMammoth)

    name = FieldProperty(IMammoth['name'])
    age = FieldProperty(IMammoth['age'])

class Edit(z3cform.EditForm):
    pass

class Index(z3cform.DisplayForm):
    fields = field.Fields(IMammoth).omit('age') 

def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

