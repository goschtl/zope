import persistent
import zope.interface
from zope.app.dublincore.interfaces import IZopeDublinCore
from versioning.demo.interfaces import IVProposal

class VProposal(persistent.Persistent):
    """A versionable Proposal"""
    
    zope.interface.implements(IVProposal)
    
    def __init__(self,title=u'',usecase=u'',concept=u'', \
                 todo=u'',issues=u''):
        self.title = title
        self.usecase = usecase
        self.concept = concept
        self.todo = todo
        self.issues = issues
        
    def setTitle(self, title):
        """Set proposal title in Dublin Core."""
        dc = IZopeDublinCore(self)
        dc.title = unicode(title)

    def getTitle(self):
        """Get proposal title in Dublin Core."""
        dc = IZopeDublinCore(self)
        return dc.title
        
    title=property(getTitle,setTitle)        

    def setUseCase(self, usecase):
        """Set proposal usecase."""
        #if usecase == 'foo': usecase = "bar" #a simple precondition  
        self.__dict__['usecase'] = usecase

    def getUseCase(self):
        """Get proposal usecase."""
        return self.__dict__['usecase']
        
    usecase=property(getUseCase,setUseCase)        

    def setConcept(self, concept):
        """Set proposal concept."""  
        self.__dict__['concept'] = concept

    def getConcept(self):
        """Get proposal concept."""
        return self.__dict__['concept']
        
    concept=property(getConcept,setConcept)
    
    def setTodo(self, todo):
        """Set proposal todo."""  
        self.__dict__['todo'] = todo

    def getTodo(self):
        """Get proposal todo."""
        return self.__dict__['todo']
        
    todo=property(getTodo,setTodo)        

    def setIssues(self, issues):
        """Set proposal issues."""  
        self.__dict__['issues'] = issues

    def getIssues(self):
        """Get proposal issues."""
        return self.__dict__['issues']
        
    issues=property(getIssues,setIssues)        
    

