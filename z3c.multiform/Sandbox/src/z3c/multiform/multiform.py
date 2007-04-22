
import copy
import zope.i18n

from zope import interface
from zope import component
from zope import formlib
from zope.formlib import namedtemplate
from zope.formlib.interfaces import IBoundAction
from zope.app import zapi
from zope.app.form.interfaces import IInputWidget, IDisplayWidget
from zope.app.form.browser.interfaces import IWidgetInputErrorView
from zope.app.i18n import ZopeMessageFactory as _

import interfaces
from interfaces import IFormLocation, ISelection


def isFormDisplayMode(f, action):
    return not f.inputMode
    
def isFormInputMode(f, action):
    return f.inputMode

def anySubFormInputMode(f, action):
    if not interfaces.IMultiForm.providedBy(f):
        f = f.parentForm
    for sf in f.subForms.values():
        if sf.inputMode:
            return True

def allSubFormsDisplayMode(f, action):
    if not interfaces.IMultiForm.providedBy(f):
        f = f.parentForm
    for sf in f.subForms.values():
        if sf.inputMode:
            return False
    return True


class ItemAction(formlib.form.Action):
    """
    An action that is rendered in the itemform object and can
    handle the toggle between input and display.
    """
    
    interface.implements(interfaces.IItemAction)

    def __init__(self, label, **options):
        self.inputMode = options.pop('inputMode', None)
        super(ItemAction,self).__init__(label, **options)


class ParentAction(formlib.form.Action):
    """
    An action that is rendered in the parent multiform object and
    is applied to all subForms. It can handle the toggle between
    input and display.
    """
    
    interface.implements(interfaces.IParentAction)

    def __init__(self, label, **options):
        self.inputMode = options.pop('inputMode', None)
        super(ParentAction,self).__init__(label, **options)
          
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

@namedtemplate.implementation(interfaces.IParentAction)
def render_submit_button(self):
    if IBoundAction.providedBy(self) and not self.available():
        return ''
    label = self.label
    if isinstance(label, zope.i18n.Message):
        label = zope.i18n.translate(self.label, context=self.form.request)
    return ('<input type="submit" id="%s" name="%s" value="%s"'
            ' class="button" />' %
            (self.__name__, self.__name__, label)
            )

class action(formlib.form.action):
    
    def update(self, success):
        action = Action(self.label, success=success, **self.options)
        name = action.__name__
        if name in self.byname.keys():
            for no, a in enumerate(self.actions):
                if a.__name__ == action.__name__:
                    self.actions[no] = action
                    self.byname[name] = action
                    break
        else:
            self.actions.append(action)
        return action
        
class itemAction(action):

    def __call__(self, success):
        action = ItemAction(self.label, success=success, **self.options)
        self.actions.append(action)
        return action


class parentAction(action):
    
    def __call__(self, success):
        action = ParentAction(self.label, success=success, **self.options)
        self.actions.append(action)
        return action


class MultiformWidgets(object):
    
    def __init__(self, inputWidget=None, displayWidget=None):
        self.inputWidget = inputWidget
        self.displayWidget = displayWidget

    def __call__(self, field, request, iface):
        if iface == IDisplayWidget:
            return self.displayWidget(field, request)
        else:
            return self.inputWidget(field, request)


def _createWidget(form_field, field, request, iface):
    if form_field.custom_widget is None:
        return component.getMultiAdapter((field, request), iface)
    else:
        if isinstance(form_field.custom_widget, MultiformWidgets):
            return form_field.custom_widget(field, request, iface)
        else:
            return form_field.custom_widget(field, request)


def setUpWidgets(form_fields,
                 form_prefix=None, context=None, request=None, form=None,
                 data=(), adapters=None, ignore_request=False):

    if request is None:
        request = form.request
    if context is None and form is not None:
        context = form.context
    if form_prefix is None:
        form_prefix = form.prefix

    widgets = []
    adapter = None
    for form_field in form_fields:
        field = form_field.field
        if form_field.render_context:
            if adapters is None:
                adapters = {}

            # Adapt context, if necessary
            interface = field.interface
            adapter = adapters.get(interface)
            if adapter is None:
                if interface is None:
                    adapter = context
                else:
                    adapter = interface(context)
                adapters[interface] = adapter
                if interface is not None:
                    adapters[interface.__name__] = adapter
            field = field.bind(adapter)
        else:
            field = field.bind(context)

        readonly = form_field.for_display
        readonly = readonly or (field.readonly and not form_field.for_input)
        readonly = readonly or (
            (form_field.render_context & formlib.form.interfaces.DISPLAY_UNWRITEABLE)
            and not formlib.form.canWrite(context, field)
            )

        if readonly:
            iface = IDisplayWidget
        else:
            iface = IInputWidget
        widget = _createWidget(form_field, field, request, iface)

#        if form_field.custom_widget is not None:
#            widget = form_field.custom_widget(field, request)
#        else:
#            if readonly:
#                widget = component.getMultiAdapter((field, request),
#                                                   IDisplayWidget)
#            else:
#                widget = component.getMultiAdapter((field, request),
#                                                   IInputWidget)

        prefix = form_prefix
        if form_field.prefix:
            prefix += '.' + form_field.prefix

        widget.setPrefix(prefix)

        if ignore_request or readonly or not widget.hasInput():
            # Get the value to render
            if form_field.__name__ in data:
                widget.setRenderedValue(data[form_field.__name__])
            elif form_field.get_rendered is not None:
                widget.setRenderedValue(form_field.get_rendered(form))
            elif form_field.render_context:
                widget.setRenderedValue(field.get(adapter))
            else:
                widget.setRenderedValue(field.default)

        widgets.append((not readonly, widget))

    return formlib.form.Widgets(widgets, len(form_prefix)+1)

        
class ItemFormBase(formlib.form.FormBase):

    interface.implements(interfaces.IItemForm)

    forceInput = []
    parentForm = None
    inputMode = None
    newInputMode = None
    form_fields=[]
    actions = []
    
    def __init__(self, context, request, parentForm):
        # we have to copy the default fields, so that we can mutate
        # them in our instance
        self.form_fields = copy.deepcopy(self.__class__.form_fields)
        self.request = request
        self.context = component.getMultiAdapter((context, self), IFormLocation)
        self.parentForm = parentForm

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            form=self, adapters=self.adapters, ignore_request=ignore_request)
        # XXX how to check for the field
        if self.widgets.get('selected'):
            widget = self.widgets['selected']
            widget.setRenderedValue(interfaces.ISelection(self.context).selected)

    def availableActions(self):
        # we need to override this, because we should not return the
        # parentActions
        if not hasattr(self, 'actions'):
            return []
        actions = [action for action in self.actions
                   if not interfaces.IParentAction.providedBy(action)]
        return formlib.form.availableActions(self, actions)
        
    def availableParentActions(self):
        if not hasattr(self, 'actions'):
            return []
        actions = [action for action in self.actions
                   if interfaces.IParentAction.providedBy(action)]
        return formlib.form.availableActions(self, actions)

    def __call__(self):
        return self.render()


class MultiFormBase(formlib.form.FormBase):

    interface.implements(interfaces.IMultiForm)

    form_fields = []
    actions = []

    itemFormFactory = ItemFormBase

    forms = []
    subForms= {}
    subActionNames = []
    subFormInputMode = {}

    def __init__(self, context, request):
        super(MultiFormBase,self).__init__(context, request)
        self.filter = self.context

    def setUpWidgets(self, ignore_request=False):
        if not ignore_request:
            self.forms = list(self.filter.keys())
            self.checkInputMode()
            self.updateSelection()
        super(MultiFormBase,self).setUpWidgets(ignore_request=ignore_request)
        self.setUpItems()

    def setUpItem(self, name, item, inputMode):
        prefix = self.prefix + '.sf.' + name
        subForm = self.newSubForm(item)
        if inputMode is not None and not inputMode:
            forceInput = self.itemFormFactory.forceInput
            for field in subForm.form_fields:
                if field.__name__ not in forceInput:
                    field.for_display=True
        subForm.inputMode = inputMode
        subForm.setPrefix(prefix)
        self.subForms[name] = subForm

    def setUpItems(self):
        self.forms = []
        self.subForms = {}
        for key, item in self.filter.items():
            self.forms.append(key)
            inputMode = self.subFormInputMode.get(key, self.itemFormFactory.inputMode)
            self.setUpItem(key, item, inputMode)
        self.refreshSubActionNames()

    def resetForm(self):
        for key in self.forms:
            form = self.subForms[key]
            inputMode = form.newInputMode
            if inputMode is not None:
                self.subFormInputMode[key] = inputMode
        self.setUpWidgets(ignore_request=True)
   
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

    def checkInputModeAction(self, action):
        if interfaces.IItemAction.providedBy(action):
            for key in self.forms:
                name = self.prefix + '.sf.' + key + action.__name__
                if name in self.request.form:
                    return action.inputMode
        if interfaces.IParentAction.providedBy(action):
            name = self.prefix + '.' + action.__name__
            if name in self.request.form:
               return action.inputMode
        return None

    def checkInputModeFields(self, key, tmpForm):
        """Returns true if any of the fields except fields in forceInput
        has input."""
        for field in tmpForm.form_fields:
            if field.__name__ not in tmpForm.forceInput:
                name = self.prefix + '.sf.' + key + '.' + field.__name__
                if name in self.request.form:
                    return True
        return False

    def checkInputMode(self):
        self.subFormInputMode = {}
        # check if any action with inputMode Flag in request
        inputMode = None
        # check itemForm actions
        if hasattr(self.itemFormFactory, 'actions'):
            for action in self.itemFormFactory.actions:
                if getattr(action, 'inputMode', None) is not None:
                    inputMode = self.checkInputModeAction(action)
                    if inputMode is not None:
                        break
        # check form actions
        if inputMode is None and hasattr(self, 'actions'):
            for action in self.actions:
                if getattr(action, 'inputMode', None) is not None:
                    inputMode = self.checkInputModeAction(action)
                    if inputMode is not None:
                        break
        if inputMode is None:
            return
        
        # check which forms in inputMode
        if len(self.forms) > 0:
            # get any inputfield
            tmpForm = self.newSubForm(self.filter[self.forms[0]])
            for key in self.forms:
                self.subFormInputMode[key] = self.checkInputModeFields(key, tmpForm)

    def updateSelection(self):
        for field in self.itemFormFactory.form_fields:
            if issubclass(field.field.interface,interfaces.ISelection):
                form_fields = formlib.form.Fields(field)
                for key, item in self.filter.items():
                    sForm = SelectionForm(item, self.request, form_fields)
                    name = self.prefix + '.sf.' + key
                    sForm.setPrefix(name)
                    sForm.form_fields = form_fields
                    sForm.setUpWidgets()
                    data = {}
                    try:
                        formlib.form.getWidgetsData(sForm.widgets, sForm.prefix, data)
                    except:
                       pass
                    formlib.form.applyChanges(sForm.context, sForm.form_fields, data)
                return

    def newSubForm(self, item):
        """creates a new instance from the itemFormFactory for item."""
        return self.itemFormFactory(item, self.request, self)

    def availableSubActions(self):
        if self.subActionNames:
            for name in self.subActionNames:
                # remove the prefix of our form because, the actions in
                # the class variable have no prefix in their name
                actionName = name[len(self.prefix)+1:]
                action = self.itemFormFactory.actions.byname[actionName]
                action = copy.copy(action)
                action.__name__ = name
                # we need the form here to render, maybe we can do
                # this somehow with an Actions object (__get__)
                action.form = self
                yield action

    def update(self):
        if self.form_reset:
            self.setUpWidgets()
            self.form_reset = False

        data = {}
        errors, action = formlib.form.handleSubmit(self.actions, data, self.validate)
        # the following part will make sure that previous error not
        # get overriden by new errors. This is usefull for subforms. (ri)
        if self.errors is None:
            self.errors = errors
        else:
            if errors is not None:
                self.errors += tuple(errors)

        if errors:
            self.status = _('There were errors')
            result = action.failure(data, errors)
        elif errors is not None:
            self.form_reset = True
            result = action.success(data)
        else:
            result = None

        self.form_result = result        
#        self.forms = list(self.filter.keys())
#        self.checkInputMode()
#        self.updateSelection()
#        super(MultiFormBase,self).update()
        # either (form update or errors) or (subforms update)
        if not (self.form_reset or self.errors):
            for key in self.forms:
                form = self.subForms[key]
                form.update()
                if form.errors:
                    self.form_reset = False
                    break
                else:
                    self.form_reset = self.form_reset or form.form_reset

    def iterSubForms(self):
        for key in self.forms:
            yield self.subForms[key]


class SelectionForm(formlib.form.FormBase):
    
    def __init__(self, context, request, form_fields):
        self.form_fields = form_fields
        self.request = request
        self.context = component.getMultiAdapter((context,self), IFormLocation)

