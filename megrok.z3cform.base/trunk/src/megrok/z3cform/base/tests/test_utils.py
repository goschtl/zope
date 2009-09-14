"""
  >>> person = Person()
  >>> IPerson.providedBy(person)
  True
  >>> person.name = u"christian"
  >>> from zope.event import notify
  >>> from zope.lifecycleevent import Attributes
  >>> notify(ObjectModifiedEvent(person, *[Attributes(IPerson, 'name')]))
  An IObjectModifiedEvent was sent for a person with the following changes:
  name  
  
"""
import grokcore.component as grok
from zope.schema import TextLine
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent


class IPerson(Interface):
    name = TextLine(title=u"Name")

class Person(grok.Context):
    grok.implements(IPerson)

    name = u""


@grok.subscribe(IPerson, ObjectModifiedEvent)
def onNameChange(context, event):
    print ("An IObjectModifiedEvent was sent for a person with the "
           "following changes:")
    for descr in event.descriptions:
        print ", ".join(descr.attributes)


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.base.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite
