import zope.interface
import zope.component
import zope.schema
import zope.formlib.form

import zc.notification.interfaces

from zc.notification.i18n import _

class PreferencesForm(zope.formlib.form.PageForm):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.utility = context

    form_fields = zope.formlib.form.FormFields(
        zc.notification.interfaces.INotificationSubscriptions,
        zc.notification.interfaces.IPreferredNotifierMethod)

    # subclasses can override/extend these two methods

    def collect_data(self):
        principal_id = self.request.principal.id
        data = {}
        data[u'notifications'] = self.utility.getRegistrations(principal_id)
        data[u'method'] = self.utility.getNotifierMethod(principal_id)
        return data

    def apply_data(self, data):
        principal_id = self.request.principal.id
        notifications = data.get(u'notifications', [])
        method = data.get(u'method', "")
        self.utility.setRegistrations(principal_id, notifications)
        self.utility.setNotifierMethod(principal_id, method)

    # but shouldn't need to override these

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = zope.formlib.form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            form=self, adapters=self.adapters,
            ignore_request=ignore_request, data=self.collect_data())

    @zope.formlib.form.action(
        _("Apply"), condition=zope.formlib.form.haveInputWidgets)
    def handle_apply(self, action, data):
        self.apply_data(data)
        self.status = _(u'Preferences Applied')
