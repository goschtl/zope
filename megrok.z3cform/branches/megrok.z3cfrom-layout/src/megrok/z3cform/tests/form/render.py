"""

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
      ...
  GrokError: It is not allowed to specify a custom 'render' method for
  form <class 'megrok.z3cform.tests.form.render.Edit'>. Forms either
  use the default template or a custom-supplied one.

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


    def render(self):
        return u"I want a carrot."


