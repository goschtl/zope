import zope.component
from zope.app.session.interfaces import ISession
from zope.app.container.interfaces import IContainer

from z3c.template.interfaces import ILayoutTemplate
from z3c.formdemo.browser import formatter
from z3c.form import form, button
from z3c.form.interfaces import IFormLayer, INPUT_MODE
from z3c.formdemo.addressbook import interfaces, browser, dateselect

SESSION_KEY = 'z3c.formdemo.addressbook'

import grok

import mars.view
import mars.layer
import mars.adapter
from mars.formdemo.layer import IDemoBrowserLayer

mars.layer.layer(IDemoBrowserLayer)


class DateSelectWidget(mars.adapter.AdapterFactory):
    mars.adapter.factory(dateselect.DateSelectDataConverter)

class ContactLabel(mars.adapter.AdapterFactory):
    grok.name('title')
    mars.adapter.factory(button.StaticButtonActionAttribute(
                        u'Add Contact', 
                        button=form.AddForm.buttons['add'], 
                        form=browser.ContactAddForm))

class AddressBook(mars.view.PageletView):
    grok.context(IContainer)
    grok.name('addressbook')

    columns = (
        browser.SelectContactColumn(
            u'Last Name', lambda i, f: i.lastName, name='lastName'),
        browser.SelectContactColumn(
            u'First Name', lambda i, f: i.firstName, name='firstName'),
        )

    @apply
    def selectedContact():
        def get(self):
            session = ISession(self.request)[SESSION_KEY]
            return session.get('selectedContact')
        def set(self, value):
            session = ISession(self.request)[SESSION_KEY]
            session['selectedContact'] = value
        return property(get, set)

    def update(self):
        # Select a new contact
        if 'selectContact' in self.request:
            self.selectedContact = self.context[self.request['selectContact']]
        # Setup the form
        if self.selectedContact:
            self.form = browser.ContactEditForm(self.selectedContact, self.request)
            self.form.update()
        if not self.selectedContact:
            self.form = browser.ContactAddForm(self.context, self.request)
            self.form.update()
        # Setup the table
        rows = [content for content in self.context.values()
                if interfaces.IContact.providedBy(content)]

        self.table = formatter.SelectedItemFormatter(
            self.context, self.request, rows,
            prefix = SESSION_KEY + '.', columns=self.columns,
            sort_on=[('lastName', False)])
        self.table.sortKey = 'z3c.formdemo.addressbook.sort-on'
        self.table.cssClasses['table'] = 'contact-list'
        self.table.widths = (150, 150)
        self.table.selectedItem = self.selectedContact

    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)

class AddressBookTemplate(mars.template.TemplateFactory):
    grok.context(AddressBook)
    grok.template('addressbook.pt')

class ContactAddTemplate(mars.template.TemplateFactory):
    grok.context(browser.ContactAddForm)
    grok.template('contact.pt')

class ContactTemplate(mars.template.TemplateFactory):
    grok.context(browser.ContactEditForm)
    grok.template('contact.pt')

class AddressesTemplate(mars.template.TemplateFactory):
    grok.context(browser.AddressesForm)
    grok.template('addresses.pt')

class AddressTemplate(mars.template.TemplateFactory):
    grok.context(browser.AddressForm)
    grok.template('address.pt')

class PhonesTemplate(mars.template.TemplateFactory):
    grok.context(browser.PhonesForm)
    grok.template('phones.pt')

class PhoneTemplate(mars.template.TemplateFactory):
    grok.context(browser.PhoneForm)
    grok.template('phone.pt')

class EmailsTemplate(mars.template.TemplateFactory):
    grok.context(browser.EMailsForm)
    grok.template('emails.pt')

class EmailTemplate(mars.template.TemplateFactory):
    grok.context(browser.EMailForm)
    grok.template('email.pt')

class DateSelectWidgetTemplate(mars.template.WidgetTemplateFactory):
    grok.context(zope.interface.Interface)
    grok.template('dateselect.pt')
    mars.template.widget(dateselect.DateSelectWidget)
    mars.template.mode(INPUT_MODE)
    mars.layer.layer(IFormLayer)

