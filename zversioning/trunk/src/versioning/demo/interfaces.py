import zope.interface
from zope.schema import Text, TextLine
from zope.i18nmessageid import MessageIDFactory
_ = MessageIDFactory("vproposal")
 
 
class IVProposal(zope.interface.Interface):
    """Provides access to a versionable Proposal""" 
    
    title = TextLine(title=_("Title"))
    usecase = Text(title=_("Use Case"))
    concept = Text(title=_("Concept"),required=False)
    todo = Text(title=_("Todo"),required=False)
    issues = Text(title=_("Open Issues"),required=False)
        
    def rusecase():
        """Render usecase to HTML"""    
        
    def rconcept():
        """Render usecase to HTML"""    

    def rtodo():
        """Render usecase to HTML"""
        
    def rissues():
        """Render usecase to HTML"""        