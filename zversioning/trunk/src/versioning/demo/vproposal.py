import persistent
import zope.interface
from zope.app.dublincore.interfaces import IZopeDublinCore
from versioning.demo.interfaces import IVProposal

class VProposal(persistent.Persistent):
    """A versionable Proposal"""
    
    zope.interface.implements(IVProposal)
    
    def __init__(self,title='',usecase='',concept='',todo='',issues=''):
        self.title = title
        self.usecase = usecase
        self.concept = concept
        self.todo = todo
        self.issues = issues
        
    def proposal(self):
        return "%s\n%s\n%s\n%s\n%s" % (self.title,self.usecase,self.concept, \
                           self.todo,self.issues)        