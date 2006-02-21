from zope.formlib import form, page

from Products.Five.browser import BrowserView
from Products.Five.formlib.formbase import AddForm, EditForm, Form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.Five.formlib.tests.content import IContent, Content

class AddContentForm(AddForm):
    """AddForm for creating and adding IContent objects
    """
    
    form_fields = form.Fields(IContent)

    def createAndAdd(self, data):
        id = 'some_id'
        ctnt = Content(id, data.get('title'), somelist=data.get('somelist'))
        self.context._setObject(id, ctnt)

class EditContentForm(EditForm):
    """EditForm for editing IContent objects
    """
    
    form_fields = form.Fields(IContent)
    