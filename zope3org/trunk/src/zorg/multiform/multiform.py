from zope.app.publisher.browser import BrowserView
from zope.interface import implements
from zope.app import zapi
from zope.app.form.browser.interfaces import IWidgetInputErrorView
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.formlib.interfaces import IBoundAction
from zope.formlib.i18n import _
from interfaces import IMultiForm, IParentAction, IFormLocation,IItemForm
from zope import interface
        

def isFormDisplayMode(f,action):
    return not f.inputMode
    
def isFormInputMode(f,action):
    return f.inputMode

def isParentFormDisplayMode(f,action):
    return not f.parentForm.inputMode

def isParentFormInputMode(f,action):
    return f.parentForm.inputMode

class ParentAction(form.Action):

    """an action that is rendered in the parent multiform object and
    is applied to all subForms"""
    
    implements(IParentAction)
    def __init__(self, label, **options):
        self.inputMode = options.pop('inputMode',None)
        super(ParentAction,self).__init__(label,**options)
        
        
    def __get__(self, form, class_=None):
        if form is None:
            return self
        result = self.__class__.__new__(self.__class__)
        result.__dict__.update(self.__dict__)
        result.form = form
        result.__name__ = form.parentForm.prefix + '.' + result.__name__
        interface.alsoProvides(result, IBoundAction)
        return result

    def submitted(self):
        # override to find the matching prefix
        if not self.available():
            res = False
        else:
            res =  self.__name__ in self.form.request
        return res


class parentAction(form.action):

    def __call__(self, success):
        action = ParentAction(self.label, success=success, **self.options)
        self.actions.append(action)
        return action


class ItemFormBase(form.FormBase):


    implements(IItemForm)
    forceInput = []
    parentForm = None
    inputMode = None

    def __init__(self,context,request,parentForm):
        self.request=request
        self.context = getMultiAdapter([context,self],IFormLocation)
        self.parentForm=parentForm

    def update(self):
        super(ItemFormBase,self).update()
        
    def availableParentActions(self):
        actions=[]
        if hasattr(self,'actions'):
            for action in self.actions:
                if IParentAction.providedBy(action):
                    actions.append(action)
                    
        actions= form.availableActions(self, actions)
        return actions

class MultiFormBase(form.FormBase):

    implements(IMultiForm)
    itemFormFactory = ItemFormBase
    subForms={}
    form_fields = []
    actions = []
    subActionNames = []
    inputMode = None
    newInputMode = None
    
    def update(self):
        self.initInputMode()
        self.checkInputMode()
        super(MultiFormBase,self).update()
        subFormReset = False
        hasErrors = False
        for form in self.subForms.values():
            form.update()
            hasErrors = hasErrors or form.errors
        if hasErrors:
            self.newInputMode=None
        if self.newInputMode is not None:
            self.setInputMode(self.newInputMode)
            self.setUpForms(ignore_request=True)

    def setUpWidgets(self, *args, **kw):
        super(MultiFormBase,self).setUpWidgets(*args,**kw)
        self.subForms = {}
        self.setUpForms(*args, **kw)

    def setUpForms(self, *args, **kw):
        for name,item in self.context.items(): 
            prefix = (self.prefix and self.prefix+'.' or '') + name
            subForm = self.itemFormFactory(item,self.request,self)
            if self.inputMode is not None and not self.inputMode \
                   and subForm.inputMode is not None and not subForm.inputMode:
                forceInput = self.itemFormFactory.forceInput
                for field in subForm.form_fields:
                    if field.__name__ not in forceInput:
                        field.for_display=True
            subForm.setPrefix(prefix)
            subForm.setUpWidgets(*args, **kw)
            self.subForms[name] = subForm
        self.refreshSubActionNames()

    def refreshSubActionNames(self):
        availableActions = set()
        for subForm in self.subForms.values():
            availableActions.update([action.__name__ for action in \
                                     subForm.availableParentActions()])
        self.subActionNames = []
        if hasattr(self.itemFormFactory,'actions'):
            for action in self.itemFormFactory.actions:
                name = '%s.%s' % (self.prefix,action.__name__)
                if name in availableActions:
                    self.subActionNames.append(name)
                    
            
    def setInputMode(self,v=True):
        if self.inputMode != v:
            self.inputMode = v
            for form in self.subForms.values():
                form.form_reset=True


    def initInputMode(self):
        self.inputMode = self.itemFormFactory.inputMode
        if self.inputMode is None:
            self.inputMode = False
            for field in self.itemFormFactory.form_fields:
                if not field.for_display:
                    self.inputMode=True
                    break

    def checkInputMode(self):
        for action in self.itemFormFactory.actions:
            name = '%s.%s' % (self.prefix,action.__name__)
            if name in self.request.form and getattr(action,
                                'inputMode', None) is not None:
                self.setInputMode(action.inputMode)
            
                
