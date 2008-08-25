"""

  >>> grok.testing.grok(__name__)

"""

from five import grok
from five.megrok import z3cform
from zope import interface, schema
from zope.schema.fieldproperty import FieldProperty

class IMammoth(interface.Interface):
    
    name = schema.TextLine(title=u"Name")
    age = schema.Int(title=u"Age")

class Mammoth(grok.Model):
    
    grok.implements(IMammoth)

    name = FieldProperty(IMammoth['name'])
    age = FieldProperty(IMammoth['age'])

class Edit(z3cform.EditForm):

    grok.context(IMammoth)
