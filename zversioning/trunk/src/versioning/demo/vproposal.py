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
        
    def setTitle(self, title):
        """Set bug title."""
        dc = IZopeDublinCore(self)
        dc.title = title

    def getTitle(self):
        """Get bug title."""
        dc = IZopeDublinCore(self)
        return dc.title
        
    title=property(getTitle,setTitle)        
