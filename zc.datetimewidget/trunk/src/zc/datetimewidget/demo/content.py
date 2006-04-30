from persistent import Persistent
from zope.interface import implements
from zope.app.container.contained import Contained
from zope.schema.fieldproperty import FieldProperty
from interfaces import IDemoContent

class DemoContent(Persistent,Contained):

    implements(IDemoContent)
    
    startDate = FieldProperty(IDemoContent['startDate'])
    endDate = FieldProperty(IDemoContent['endDate'])
    
    startDatetime = FieldProperty(IDemoContent['startDatetime'])
    endDatetime = FieldProperty(IDemoContent['endDatetime'])
    
