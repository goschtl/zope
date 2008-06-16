from zope import interface
from zope.security.proxy import removeSecurityProxy
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from google.interfaces import IOrganization

class ContainerVocabulary(SimpleVocabulary):
    interface.classProvides(IVocabularyFactory)
    
    #specify here an item IF, like IMentor
    filter = None
    
    def __init__(self, context):
        terms = [self.objToTerm(objekt)
                 for name, objekt
                 in self.getContainer(context).items()
                 if self.filter.providedBy(objekt)]
        
        SimpleVocabulary.__init__(self, terms)
    
    def objToTerm(self, objekt):
        return SimpleTerm(removeSecurityProxy(objekt),
                          token=objekt.__name__,
                          title=objekt.__name__)
    
    def getContainer(self, context):
        while True:
            #walk up until we reach IOrganization
            if context is None:
                raise ValueError("something is wrong")
            if IOrganization.providedBy(context):
                return context
            context=context.__parent__

from google.interfaces import IProject

class ConcreteVocabulary(ContainerVocabulary):
    filter = IProject
