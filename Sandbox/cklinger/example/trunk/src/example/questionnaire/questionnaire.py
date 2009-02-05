import grok
import persistent
import zope.interface
from zope.location import location
from zope.schema.fieldproperty import FieldProperty
import interfaces

class Questionnaire(grok.Model):
    zope.interface.implements(interfaces.IQuestionnaire)

    name = FieldProperty(interfaces.IQuestionnaire['name'])
    age = FieldProperty(interfaces.IQuestionnaire['age'])
    zope2 = FieldProperty(interfaces.IQuestionnaire['zope2'])
    plone = FieldProperty(interfaces.IQuestionnaire['plone'])
    zope3 = FieldProperty(interfaces.IQuestionnaire['zope3'])
    five = FieldProperty(interfaces.IQuestionnaire['five'])
    contributor = FieldProperty(interfaces.IQuestionnaire['contributor'])
    years = FieldProperty(interfaces.IQuestionnaire['years'])
    zopeId = FieldProperty(interfaces.IQuestionnaire['zopeId'])

    def __init__(self, **kw):
        for name, value in kw.items():
            setattr(self, name, value)

