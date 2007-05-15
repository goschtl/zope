import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.publisher import browser
from zope.pagetemplate.interfaces import IPageTemplate
from zope.schema.fieldproperty import FieldProperty

from z3c.form import form
from z3c.form import button, util

from z3c.formjs import interfaces
from z3c.formjs.i18n import MessageFactory as _

class DisplayAndEditForm(form.Form):

    zope.interface.implements(interfaces.IJSForm)

    buttons = button.Buttons(
        apply=button.Button(_('Apply'))
        )

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    @button.handler(buttons['apply'])
    def handleApply(self, action):
        data, errors = self.widgets.extract()
        if errors:
            self.status = self.formErrorsMessage
            return
        changed = applyChanges(self, data)
        if changed:
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(self.context))
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage
