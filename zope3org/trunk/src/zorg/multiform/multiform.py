from zope.app.publisher.browser import BrowserView
from zope.interface import implements

from zope.app import zapi
from zope.app.form.browser.interfaces import IWidgetInputErrorView

from zope.formlib import form
from zope.formlib.interfaces import IBoundAction
from zope.formlib.i18n import _
from interfaces import IMultiForm
from zope import interface

class ParentAction(form.Action):

    """an action that is rendered in the parent multiform object and
    is applied to all subForms"""

    def __get__(self, form, class_=None):
        if form is None:
            return self
        result = self.__class__.__new__(self.__class__)
        result.__dict__.update(self.__dict__)
        result.form = form
        #result.__name__ = form.prefix + '.' + result.__name__
        interface.alsoProvides(result, IBoundAction)
        return result

    def submitted(self):
        # override to find the matching prefix
        if not self.available():
            return False
        form = self.form.parentForm
        name = "%s.%s" % (form.prefix, self.__name__)
        return name in form.request.form


class parentAction(form.action):

    def __call__(self, success):
        action = ParentAction(self.label, success=success, **self.options)
        self.actions.append(action)
        return action


class ItemFormBase(form.FormBase):

    parentForm = None

    def __init__(self,context,request,parentForm):
        super(ItemFormBase,self).__init__(context,request)
        self.parentForm=parentForm



class MultiFormBase(form.FormBase):


    itemFormFactory = ItemFormBase
    subForms={}
    form_fields = []


    def update(self):
        super(MultiFormBase,self).update()
        for form in self.subForms.values():
            form.update()

    def setUpWidgets(self, *args, **kw):
        super(MultiFormBase,self).setUpWidgets(*args,**kw)
        self.subForms = {}
        self.setUpForms(*args, **kw)

    def setUpForms(self, *args, **kw):
        for name,item in self.context.items():
            prefix = (self.prefix and self.prefix+'.' or '') + name
            subForm = self.itemFormFactory(item,self.request,self)
            subForm.setPrefix(prefix)
            subForm.setUpWidgets(*args, **kw)
            self.subForms[name] = subForm


