from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from helpers import add_and_edit
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import implements
from interfaces import ISimpleContent, ICallableSimpleContent,\
     IIndexSimpleContent

class SimpleContent(SimpleItem):
    implements(ISimpleContent)

    meta_type = 'Five SimpleContent'
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

    tales_traversal = PageTemplateFile(
        "tales_traversal.pt", globals(),
        __name__ = 'tales_traversal')

InitializeClass(SimpleContent)

class CallableSimpleContent(SimpleItem):
    """A Viewable piece of content"""
    implements(ICallableSimpleContent)

    meta_type = "Five CallableSimpleContent"

    def __call__(self, *args, **kw):
        """ """
        return "Default __call__ called"

class IndexSimpleContent(SimpleItem):
    """A Viewable piece of content"""
    implements(IIndexSimpleContent)

    meta_type = 'Five IndexSimpleContent'

    def index_html(self, *args, **kw):
        """ """
        return "Default index_html called"


manage_addSimpleContentForm = PageTemplateFile(
    "www/simpleContentAdd", globals(),
    __name__ = 'manage_addSimpleContentForm')

def manage_addSimpleContent(self, id, title, REQUEST=None):
    """Add the simple content."""
    id = self._setObject(id, SimpleContent(id, title))
    add_and_edit(self, id, REQUEST)
    return ''

def manage_addCallableSimpleContent(self, id, title, REQUEST=None):
    """Add the viewable simple content."""
    id = self._setObject(id, CallableSimpleContent(id, title))
    add_and_edit(self, id, REQUEST)
    return ''

def manage_addIndexSimpleContent(self, id, title, REQUEST=None):
    """Add the viewable simple content."""
    id = self._setObject(id, IndexSimpleContent(id, title))
    add_and_edit(self, id, REQUEST)
    return ''
