import os.path
import zope.interface
from z3c.form import form, button, field
from z3c.form.interfaces import IField, IWidgets
from z3c.formui import layout
from z3c.formjs import jsbutton, jsevent, jsvalidator, interfaces


class IFields(zope.interface.Interface):
    zip = zope.schema.Int(
        title=u"File",
        description=u"The file to show.",
        required=True)


class ValidatorForm(
    layout.FormLayoutSupport, jsvalidator.MessageValidator, form.Form):

    zope.interface.implements(interfaces.IAJAXValidator)
    fields = field.Fields(IFields)

    @jsevent.handler(IField, event=jsevent.CHANGE)
    def fieldValidator(self, id):
        return self.ValidationRenderer(self, id).render()

    def updateWidgets(self):
        '''See interfaces.IForm'''
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()
