import zope.formlib.form

import zc.notification.email.interfaces

class EditNotifierForm(zope.formlib.form.EditForm):

    form_fields = zope.formlib.form.FormFields(
        zc.notification.email.interfaces.IEmailNotifier)
