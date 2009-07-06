"""
  >>> person = Person()
  >>> IPerson.providedBy(person)
  True
  >>> person.name = u"christian"
  >>> from zope.lifecycleevent import Attributes
  >>> grok.notify(grok.ObjectModifiedEvent(person, *[Attributes(IPerson, 'name')]))
  An IObjectModifiedEvent was sent for a person with the following changes:
  name  
  
"""
import grok
from zope.interface import Interface
from zope.schema import TextLine 

class IPerson(Interface):
    name = TextLine(title=u"Name")

class Person(grok.Model):
    grok.implements(IPerson)

    name = u""


@grok.subscribe(IPerson, grok.IObjectModifiedEvent)
def onNameChange(context, event):
    print ("An IObjectModifiedEvent was sent for a person with the "
           "following changes:")
    for descr in event.descriptions:
        print ", ".join(descr.attributes)


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite
