import persistent
import zope.interface
from zope.app.dublincore.interfaces import IZopeDublinCore
from versioning.demo.interfaces import IVProposal

class VProposal(persistent.Persistent):
    """A versionable Proposal"""
    
    zope.interface.implements(IVProposal)
    
    def __init__(self,title=u'',usecase=u'',concept=u'',todo=u'',issues=u''):
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

        