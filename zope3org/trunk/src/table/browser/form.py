
from zope.interface import implements

from zope.formlib import form
from zope.formlib.i18n import _

from interfaces import ITableForm


class RowFormBase(form.FormBase):

    actions = ()

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request
            )

    def __init__(self, view, mode, **kwargs):
        super(RowFormBase,self).__init__(view.context, view.request)
        self.view = view
        self.row = view.row
        self.table = view.row.table
        self.mode = mode
        self.setPrefix(view.prefix)

        # build up form_fields
        # kwargs includes form relevant parameters
        self.form_fields = form.Fields()
        for cellView in view.getCells():
            if cellView.useForm:
                field = cellView.field               
                fieldkwargs = {}
                fieldkwargs['for_display'] = not(mode == 'edit' and cellView.cell.selected)
                self.form_fields = self.form_fields + form.Fields(form.Field(field, **fieldkwargs),**kwargs)


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

    def setPrefix(self, prefix):
        self.prefix = prefix

    def setMode(self):
        if "%s.actions.apply" % self.prefix in self.request.form:
            self.mode = 'edit'
        
    def setNewMode(self):
        if self.newmode is not None:
            self.mode = self.newmode
            self.newmode = None
            self.form_reset = True
        
    def setUpForms(self, ignore_request=False):
        self.forms = {}
        for row in self.view.getRows():
                kwargs = {
                    'omit_readonly':False,
                    'render_context':True}
                self.forms[row.row.key] = (
                    RowFormBase(row, self.mode, **kwargs))
                
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
        # request.form set the mode
        self.setMode()
        
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

        for fo in self.forms.values():
            fo.update()
            self.form_reset = self.form_reset or fo.form_reset
            
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

    def __call__(self):
        self.update()
        return self.render()

