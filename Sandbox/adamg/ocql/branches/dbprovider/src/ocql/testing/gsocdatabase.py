
from ocql.database import metadata
from zope.interface import implements
from zope.component import adapts
from ocql.interfaces import IDB
import ocql.tests.test_zope

class GsocMetadata(metadata.Metadata):
    implements(IDB)
    adapts(None)
    
    db = {
          }
    
    classes = {
               }
    
    def __init__(self, context=None):
        import pydevd;pydevd.settrace()
        db = ocql.tests.test_zope.db
        classes = ocql.tests.test_zope.classes

    def getAll(self, klass):
        x=self.db[klass]
        return x

    def get_class(self, name):
        return self.classes[name]