import grok
import megrok.z3cform.base

#
import contact
import interfaces
import datetime

#
from z3c.form import field, form, button, widget
from examplemegrokz3cform.app import Examplemegrokz3cform
from grokcore.component import global_adapter
from z3c.form.interfaces import IAddForm


class ContactAddForm(megrok.z3cform.base.PageAddForm):
    """ A sample add form."""
    grok.context(Examplemegrokz3cform)

    label = u'Contact Add Form'
    fields = field.Fields(interfaces.IContact)

    def create(self, data):
        return contact.Contact(**data)

    def add(self, object):
        count = 0
        while 'contact-%i' %count in self.context:
            count += 1;
        self._name = 'contact-%i' %count
        self.context[self._name] = object
        return object

    def nextURL(self):
        return self.redirect(self.url(self.context[self._name]))


class ContactEditForm(megrok.z3cform.base.PageEditForm):
    grok.context(contact.Contact)
    grok.name('edit.html')
    form.extends(form.EditForm)
    label = u'Contact Edit Form'
    fields = field.Fields(interfaces.IContact)

    @button.buttonAndHandler(u'Apply and View', name='applyView')
    def handleApplyView(self, action):
        self.handleApply(self, action)
        if not self.widgets.errors:
            self.redirect(self.url(self.context, name='index'))


class ContactDisplayForm(megrok.z3cform.base.PageDisplayForm):
    """ A simple Display Form"""
    grok.context(contact.Contact)
    grok.name('index')
    template = grok.PageTemplateFile('display.pt')

    fields = field.Fields(interfaces.IContact)


