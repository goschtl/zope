from zope.interface import implements

from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from interfaces import ISimpleContent
from helpers import add_and_edit

class SimpleContent(SimpleItem):
    """A Simple Content"""

    implements(ISimpleContent)
    meta_type = 'SimpleContent'

    def __init__(self, id, title):
        self.id = id
        self.title = title

    def mymethod(self):
        """A public method"""
        return "Hello world"

    def myprivatemethod(self):
        """A private method"""
        return "Hello private world"

    def myprotectedmethod(self):
        """A protected method"""
        return "Hello protected world"

manage_addSimpleContentForm = PageTemplateFile(
    "www/simpleContentAdd", globals(),
    __name__ = 'manage_addSimpleContentForm')

def manage_addSimpleContent(self, id, title, REQUEST=None):
    """Add the simple content."""
    id = self._setObject(id, SimpleContent(id, title))
    add_and_edit(self, id, REQUEST)
    return ''
