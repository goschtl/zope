from zope.formlib import form
from interfaces import IAjaxForm
from zope import interface

class AjaxForm(form.FormBase):

    """base ajax form class which makes its widgets locatable"""

    interface.implements(IAjaxForm)
    actions = form.Actions()
    
    def setUpWidgets(self,*args,**kw):
        super(AjaxForm,self).setUpWidgets(*args,**kw)
        for widget in self.widgets:
            widget.__form__ = self
            
    def renderDisplay(self):

        return "display"

    def renderInput(self):

        return "input"

    def publishTraverse(self, request, name):
        raise NotFound(self, name, request)



    
    
