from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from helpers import add_and_edit
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Five.api import Viewable
from zope.interface import implements
from interfaces import ISimpleContent

class SimpleContent(SimpleItem, Viewable):

    implements(ISimpleContent)
    
    meta_type = 'TestSimpleContent'
    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self.title = title
        
    security.declarePublic('mymethod')
    def mymethod(self):
        return "Hello world"

    security.declarePublic('direct')
    def direct(self):
        """Should be able to traverse directly to this as there is no view.
        """
        return "Direct traversal worked"
    
InitializeClass(SimpleContent)

manage_addSimpleContentForm = PageTemplateFile(
    "www/simpleContentAdd", globals(),
    __name__ = 'manage_addSimpleContentForm')

def manage_addSimpleContent(self, id, title, REQUEST=None):
    """Add the simple content."""
    id = self._setObject(id, SimpleContent(id, title))
    add_and_edit(self, id, REQUEST)
    return ''
