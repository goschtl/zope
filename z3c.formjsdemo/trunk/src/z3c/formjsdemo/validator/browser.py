import os.path
import zope.interface
import zope.schema
from z3c.form import form, button, field
from z3c.form.interfaces import IWidgets
from z3c.formui import layout
from z3c.formjs import jsaction, jsevent, jsvalidator, interfaces


class IFields(zope.interface.Interface):
    zip = zope.schema.Int(
        title=u"ZIP",
        description=u"The Zip code.",
        required=True)


class ValidatorForm(
    layout.FormLayoutSupport, jsvalidator.MessageValidator, form.Form):

    zope.interface.implements(interfaces.IAJAXValidator)
    fields = field.Fields(IFields)
    label = u'JavaScript AJAX Validation'

    @jsaction.handler(zope.schema.interfaces.IField, event=jsevent.CHANGE)
    def fieldValidator(self, event, selector):
        return self.ValidationScript(self, selector.widget).render()

    def updateWidgets(self):
        '''See interfaces.IForm'''
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()
