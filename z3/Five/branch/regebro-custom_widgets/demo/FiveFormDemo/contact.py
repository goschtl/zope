import re
from zope.interface import Interface, implements
from zope.schema import TextLine, Choice, Int

class ISimpleContact(Interface):
    salutation = Choice(title=u'Salutation', values=("Mr.", "Mrs.", "Captain", "Don"))
    contactname = TextLine(title=u'Name')
    mailaddress = TextLine(title=u'E-Mail Address', required=0)
    age = Int(title=u'Your age')
    postal_code = TextLine(title=u'Postal code',
         constraint=re.compile("\d{5,5}(-\d{4,4})?$").match)

class SimpleContact:
    implements(ISimpleContact)
    def __init__(self, mailaddress=None, contactname=None):
        self.mailaddress = mailaddress
        self.contactname = contactname

