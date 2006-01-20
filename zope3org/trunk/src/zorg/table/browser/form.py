
from zope.interface import implements

from zope.app import zapi
from zope.app.form.browser.interfaces import IWidgetInputErrorView

from zope.formlib import form
from zope.formlib.i18n import _

from interfaces import ITableForm


def availableActions(form, actions):
    result = []
    for action in actions:
        if not action.label in form.table.config.actions:
            continue
        condition = action.condition
        if condition is not None:
            if not condition(form, action):
                continue
        result.append(action)
    return result


class TableAction(form.Action):

    def render(self):
#        if self.label in self.form.table.config.actions and \
#           not self.form.table.config.actions[self.label].isLocal:
#            return super(TableAction,self).render()
#        else:
#            return ""
        return super(TableAction,self).render()


class RowAction(form.Action):

    def render(self):
#        if self.label in self.form.table.config.actions and \
#           self.form.table.config.actions[self.label].isLocal:
#            return super(RowAction,self).render()
#        else:
#            return ""
        return super(RowAction,self).render()


class rowAction(form.action):
    
    def __call__(self, success):
        action = RowAction(self.label, success=success, **self.options)
        self.actions.append(action)
        return action


class tableAction(form.action):
    
    def __call__(self, success):
        action = TableAction(self.label, success=success, **self.options)
        self.actions.append(action)
        return action


def isRowEditMode(form, action):
    return form.mode == 'edit' and action.label in form.table.config.actions and form.row.selected


def isRowDisplayMode(form, action):
    return form.mode == 'display' and action.label in form.table.config.actions


class RowFormBase(form.FormBase):

    newmode = None

    def __init__(self, view, mode, **kwargs):
        super(RowFormBase,self).__init__(view.context, view.request)
        self.view = view
        self.row = view.row
        self.table = view.row.table
        self.mode = mode
        self.setPrefix(view.prefix)
        self.baseRow_actions = form.Actions()
        
        # build up form_fields
        # kwargs includes form relevant parameters
        self.form_fields = form.Fields()
        for cellView in view.getCells():
            if cellView.useForm:
                field = cellView.field
                isDisplay = not(mode == 'edit' and cellView.cell.selected)
                fieldkwargs = {}
                fieldkwargs['for_display'] = isDisplay
                if not isDisplay and cellView.widget is not None:
                    fieldkwargs['custom_widget'] = cellView.widget
                self.form_fields = self.form_fields + form.Fields(form.Field(field, **fieldkwargs),**kwargs)
        
    def actions():
        def _getActions(self):
            return self.baseRow_actions
        return property(_getActions)
    
    actions = actions()

    def availableActions(self, actions=None):
        if actions is not None:
            return availableActions(self, actions)
        else:
            return availableActions(self, self.actions)

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request
            )


def isFormEditMode(form, action):
    return form.mode == 'edit' and action.label in form.table.config.actions


def isFormDisplayMode(form, action):
    return form.mode == 'display' and action.label in form.table.config.actions


class TableFormBase(object):
    
    implements(ITableForm)

    label = u''

    prefix = 'grid'

    status = ''

    errors = ()

    forms = {}

    mode = 'display'

    newmode = None

    def __init__(self, view):
        self.context = view.context
        self.view = view
        self.table = view.table
        self.request = view.request
        self.prefix = view.table.config.prefix   
        self.base_actions = form.Actions()

    def actions():
        def _getActions(self):
            return self.base_actions
        return property(_getActions)
    
    actions = actions()

    def availableActions(self, actions=None):
        if actions is not None:
            return availableActions(self, actions)
        else:
            return availableActions(self, self.actions)

    def setPrefix(self, prefix):
        self.prefix = prefix

    def checkEditMode(self, prefix):
        if "%s.actions.apply" % prefix in self.request.form:
            self.mode = 'edit'
        
    def setNewMode(self):
        if self.newmode is not None:
            self.mode = self.newmode
            self.newmode = None
            self.form_reset = True

    def rowForm(self, row, **kwargs):
        return RowFormBase(row, self.mode, **kwargs)

    def setUpForms(self, ignore_request=False):
        self.forms = {}
        for row in self.view.getRows():
                if not ignore_request:
                    # check edit mode with row actions
                    self.checkEditMode(row.prefix)
                kwargs = {
                    'omit_readonly':False,
                    'render_context':True}
                self.forms[row.row.key] = self.rowForm(row, **kwargs)
                
    def resetForm(self):
        self.setUpForms(ignore_request=True)
        for fo in self.forms.values():
            fo.resetForm()

    def validate(self, action, data):
#        return (getFormsData(self.widgets, self.prefix, data)
#                + checkInvariants(self.form_fields, data))
        return ()

#    def availableActions(self):
#        return availableActions(self, self.actions)

    form_result = None
    form_reset = True

    def update(self):
        # check edit mode with table actions
        self.checkEditMode(self.prefix)
        
        self.setUpForms()
        self.form_reset = False

        data = {}
        errors, action = form.handleSubmit(self.actions, data, self.validate)
        self.errors = errors

        if errors:
            self.status = _('There were errors')
            result = action.failure(data, errors)
        elif errors is not None:
            result = action.success(data)
        else:
            result = None
        result = None     

        self.form_result = result

        if not errors:
            for fo in self.forms.values():
                fo.update()
                if fo.errors:
                    self.errors = list(self.errors) + list(fo.errors)
                self.form_reset = self.form_reset or fo.form_reset
                if fo.newmode is not None:
                    self.newmode = fo.newmode

            if self.errors:
                self.status = _('There were errors')
                self.form_reset = False
                self.newmode = None

        # if actions toggle the mode
        self.setNewMode()

        if self.form_reset:
            # build up new forms
            self.resetForm()
            form_reset = False
          
    def render(self):
        # if the form has been updated, it will already have a result
        if self.form_result is None:
            if self.form_reset:
                # we reset, in case data has changed in a way that
                # causes the widgets to have different data
                self.resetForm()
                for fo in self.forms.values():
                    fo.form_reset = True
                self.form_reset = False
            for fo in self.forms.values():
                fo.render()
            self.form_result = self.template()

        return self.form_result

    def error_views(self):
        for error in self.errors:
            if isinstance(error, basestring):
                yield error
            else:
                view = zapi.getMultiAdapter(
                    (error, self.request),
                    IWidgetInputErrorView)
                title = getattr(error, 'widget_title', None) # XXX duck typing
                if title:
                    yield '%s: %s' % (title, view.snippet())
                else:
                    yield view.snippet()
                    
    def handOverAction(self, name, label):
        """hand over action table action to row actions with same name, label
           of all selected rows."""
        selected = False
        for fo in self.forms.values():
            if fo.row.selected:
                # hand over submit of action to all forms
                action = "%s.actions.%s" % (fo.prefix, name)
                self.request.form[action] = label
                selected = True
        return selected
        
    def __call__(self):
        self.update()
        return self.render()

