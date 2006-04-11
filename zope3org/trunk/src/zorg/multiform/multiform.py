from zope.app.publisher.browser import BrowserView
from zope.interface import implements
from zope.app import zapi
from zope.app.form.browser.interfaces import IWidgetInputErrorView
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.formlib.interfaces import IBoundAction
from zope.formlib.i18n import _
from interfaces import IMultiForm, IParentAction, IItemAction, ISelection
from interfaces import IFormLocation,IItemForm
import copy
from zope.formlib import namedtemplate
import zope.i18n
from zope import interface
        

def isFormDisplayMode(f,action):
    return not f.inputMode
    
def isFormInputMode(f,action):
    return f.inputMode

def isParentFormDisplayMode(f,action):
    return not isParentFormInputMode(f,action)

def isParentFormInputMode(f,action):
    return (True in f.parentForm.subFormInputMode.values())

def anySubFormInputMode(form,action):
    if not IMultiForm.providedBy(form):
        form = form.parentForm
    return (True in form.subFormInputMode.values())

def allSubFormDisplayMode(form,action):
    if not IMultiForm.providedBy(form):
        form = form.parentForm
    return not (True in form.subFormInputMode.values())


class ItemAction(form.Action):

    """an action that is rendered in the itemform object and can
    handle the toggle between input and display."""
    
    implements(IItemAction)
    def __init__(self, label, **options):
        self.inputMode = options.pop('inputMode',None)
        super(ItemAction,self).__init__(label,**options)
    
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

@namedtemplate.implementation(IParentAction)
def render_submit_button(self):
    if IBoundAction.providedBy(self) and not self.available():
        return ''
    label = self.label
    if isinstance(label, (zope.i18n.Message, zope.i18n.MessageID)):
        label = zope.i18n.translate(self.label, context=self.form.request)
    return ('<input type="submit" id="%s" name="%s" value="%s"'
            ' class="button" />' %
            (self.__name__, self.__name__, label)
            )



class itemAction(form.action):

    def __call__(self, success):
        action = ItemAction(self.label, success=success, **self.options)
        self.actions.append(action)
        return action

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
    newInputMode = None
    form_fields=[]
    actions = []

    def __init__(self,context,request,parentForm):
        # we have to copy the default fields, so that we can mutate
        # them in our instance
        self.form_fields = copy.deepcopy(self.__class__.form_fields)
        self.request = request
        self.context = getMultiAdapter([context,self],IFormLocation)
        self.parentForm = parentForm

    def update(self):
        super(ItemFormBase,self).update()

    def availableActions(self):
        # we need to override this, because we should not return the
        # parentActions
        if not hasattr(self,'actions'):
            return []
        actions = [action for action in self.actions
                   if not IParentAction.providedBy(action)]
        return form.availableActions(self, actions)
        
    def availableParentActions(self):
        if not hasattr(self,'actions'):
            return []
        actions = [action for action in self.actions
                   if IParentAction.providedBy(action)]
        return form.availableActions(self, actions)

class MultiFormBase(form.FormBase):

    implements(IMultiForm)
    itemFormFactory = ItemFormBase
    subForms={}
    form_fields = []
    actions = []
    subActionNames = []
    subFormInputMode = {}
    selection = []
    actions = []
    
    def update(self):
        self.checkInputMode()
        self.updateSelection()
        super(MultiFormBase,self).update()
        hasErrors = False
        for form in self.subForms.values():
            form.update()
        refresh = False
        for form in self.subForms.values():
            if form.newInputMode is not None:
                newInputMode = form.newInputMode
                context = self.context[form.context.__name__]
                name = context.__name__
                self.setUpForm(name, context, newInputMode)
                self.subFormInputMode[name] = newInputMode
                refresh = True
            if refresh:
                self.refreshSubActionNames()

    def setUpWidgets(self, *args, **kw):
        super(MultiFormBase,self).setUpWidgets(*args,**kw)
        self.subForms = {}
        self.setUpForms(*args, **kw)

    def setUpForm(self, name, item, inputMode, *args, **kw):
        prefix = (self.prefix and self.prefix+'.' or '') + name
        subForm = self.newSubForm(item)
        if inputMode is not None and not inputMode:
            forceInput = self.itemFormFactory.forceInput
            for field in subForm.form_fields:
                if field.__name__ not in forceInput:
                    field.for_display=True
        subForm.inputMode = inputMode
        subForm.setPrefix(prefix)
        subForm.setUpWidgets(*args, **kw)
        self.subForms[name] = subForm

    def setUpForms(self, *args, **kw):
        for name,item in self.context.items():
            inputMode = self.subFormInputMode.get(name,self.itemFormFactory.inputMode)
            self.setUpForm(name, item, inputMode)
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
                    
            
    def checkInputMode(self):
        self.subFormInputMode = {}
        inputMode = None
        for action in self.itemFormFactory.actions:
            name = '%s.%s' % (self.prefix,action.__name__)
            if name in self.request.form and getattr(action,
                                'inputMode', None) is not None:
                inputMode = action.inputMode
                break
        if inputMode is None:
            return
        inputField = None
        if len(self.context) > 0:
            for name, item in self.context.items():
                break
            tmpForm = self.newSubForm(item)
            for field in tmpForm.form_fields:
                if not field.for_display and field.__name__ not in tmpForm.forceInput:
                    inputField = field
                    break
            for name in self.context.keys():
                prefix = self.prefix + '.' + name + '.' + field.__name__
                self.subFormInputMode[name] = (prefix in self.request.form)
                
    def updateSelection(self):
        for field in self.itemFormFactory.form_fields:
            if issubclass(field.field.interface,ISelection):
                form_fields = form.Fields(field)
                for name,item in self.context.items():
                    sForm = SelectionForm(item, self.request, form_fields)
                    prefix = (self.prefix and self.prefix+'.' or '') + name
                    sForm.setPrefix(prefix)
                    sForm.form_fields = form_fields
                    sForm.setUpWidgets()
                    data = {}
                    try:
                        form.getWidgetsData(sForm.widgets, sForm.prefix, data)
                    except:
                       pass
                    form.applyChanges(sForm.context, sForm.form_fields, data)
                return

    def newSubForm(self,item):

        """creates a new instance from the itemFormFactory for
        temporary usage"""
        
        return self.itemFormFactory(item,self.request,self)

    def availableSubActions(self):
        if self.subActionNames:
            for name in self.subActionNames:
                # remove the prefix of our form because, the actions in
                # the class variable have no prefix in their name
                actionName = name[len(self.prefix)+1:]
                action = self.itemFormFactory.actions.byname[actionName]
                action = copy.copy(action)
                action.__name__ = name
                yield action

    
class SelectionForm(form.FormBase):
    
    def __init__(self, context, request, form_fields):
        self.form_fields = form_fields
        self.request = request
        self.context = getMultiAdapter([context,self],IFormLocation)
