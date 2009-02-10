from zope import component
from zope.app.intid.interfaces import IIntIds
from zope.interface import implements
from zc.sourcefactory.interfaces import ITokenPolicy, ISourcePolicy
from zc.sourcefactory.policies import BasicTermPolicy
from zc.sourcefactory.factories import BasicSourceFactory
from z3c.objpath.interfaces import IObjectPath
from z3c.relationfield import RelationValue

from z3c.relationfieldui.interfaces import IRelationValuePolicy
        
class RelationValuePolicy(object):
    implements(IRelationValuePolicy)
    
    def getTargets(self):
        raise NotImplementedError

    def getValues(self):
        getId = component.getUtility(IIntIds).getId
        return [RelationValue(getId(target)) for target in self.getTargets()]

    def filterValue(self, value):
        return True

class RelationTokenPolicy(object):
    implements(ITokenPolicy)
    
    def getToken(self, value):
        return value.to_path    

    def getValue(self, source, token):
        resolve = component.getUtility(IObjectPath).resolve
        try:
            obj = resolve(token)
        except ValueError:
            result = RelationValue(None)
            result.broken(token)
            return result
        getId = component.getUtility(IIntIds).getId
        return RelationValue(getId(obj))

class RelationTermPolicy(BasicTermPolicy):
    def getTitle(self, value):
        return value.to_path

class RelationSourceFactory(BasicSourceFactory,
                            RelationValuePolicy, RelationTokenPolicy,
                            RelationTermPolicy):
    implements(ISourcePolicy)
