"""

  >>> grok.testing.grok(__name__)
  >>> manfred = Mammoth()

  >>> from zope import component
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  Check that fields have been created on the edition page:

  >>> view = component.getMultiAdapter((manfred, request), name='edit')
  >>> len(view.fields)
  2
  >>> [field.__name__ for field in view.fields.values()]
  ['name', 'age']
  

  And on the display page:

  >>> view = component.getMultiAdapter((manfred, request), name='index')
  >>> len(view.fields)
  2
  >>> [field.__name__ for field in view.fields.values()]
  ['name', 'age']


"""

import grok

from zope import interface, schema
from zope.schema.fieldproperty import FieldProperty
from megrok import z3cform

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
    pass


