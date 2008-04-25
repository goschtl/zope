##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Address Book Views

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.location
from zope.app.container import btree
from zope.session.interfaces import ISession
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher import browser
from zope.traversing.browser import absoluteURL
from zope.viewlet.viewlet import CSSViewlet, JavaScriptViewlet
from z3c.template.interfaces import ILayoutTemplate
from zc.table import column
from zc.table.interfaces import ISortableColumn

from z3c.form import form, field, button, subform
from z3c.formdemo.browser import formatter
from z3c.formdemo.addressbook import interfaces, contact, dateselect

SESSION_KEY = 'z3c.formdemo.addressbook'

AddressBookCSSViewlet = CSSViewlet('addressbook.css')
TextShadowViewlet = JavaScriptViewlet('text-shadow.js')


class AddressForm(subform.EditSubForm, form.EditForm):

    form.extends(subform.EditSubForm)
    fields = field.Fields(interfaces.IAddress)
    name = None
    deleted = False

    # In this application, we do not want this message
    noChangesMessage = None

    def updateWidgets(self):
        super(AddressForm, self).updateWidgets()
        for name, widget in self.widgets.items():
            widget.addClass(name)

    @property
    def title(self):
        return interfaces.AddressNamesVocabulary.getTerm(self.name).title

    @button.handler(form.AddForm.buttons['add'])
    def handleAdd(self, action):
        self.handleApply(self, action)

    @button.buttonAndHandler(u'Delete')
    def handleDelete(self, action):
        addresses = self.getContent().__parent__
        del addresses[self.name]
        self.deleted = True


class AddressesForm(form.AddForm):
    """Form to manage addresses."""
    # Select the field that specifies the address name.
    fields = field.Fields(interfaces.IContact['addresses'].key_type)
    parentForm = None

    def create(self, data):
        address = contact.Address()
        address.__name__ = data['addressName']
        return address

    def add(self, object):
        addressbook = self.getContent()
        # Make sure that an address cannot be added twice.
        if object.__name__ in addressbook:
            self.status = u'Address already provided for contact.'
            return None
        addressbook[object.__name__] = object
        return object

    def getContent(self):
        # Get the address container from the contact
        if interfaces.IContact.providedBy(self.context):
            return self.context.addresses
        # We are in the process of adding a contact, so store the addresses
        # container in a session variable.
        session = ISession(self.request)[SESSION_KEY]
        if 'addresses' not in session:
            session['addresses'] = btree.BTreeContainer()
        return session['addresses']

    def update(self):
        # Make sure that we have a unique prefix.
        self.prefix = self.parentForm.prefix + 'addresses.'
        super(AddressesForm, self).update()
        # For each address, create an address form.
        self.addressForms = []
        for name, address in self.getContent().items():
            form = AddressForm(address, self.request, self.parentForm)
            form.name = str(name)
            # The prefix is created at runtime to guarantee uniqueness
            form.prefix = self.prefix + str(name) + '.'
            form.update()
            # Updating the address can also mean its deletion. If deleted, it
            # is not added to the list.
            if not form.deleted:
                self.addressForms.append(form)

    def render(self):
        # Boilerplate when workign with view templates.
        template = zope.component.getMultiAdapter(
            (self, self.request), IPageTemplate)
        return template(self)


class PhoneForm(subform.EditSubForm):
    form.extends(subform.EditSubForm)
    fields = field.Fields(interfaces.IPhone)
    attrName = None
    error = None
    mode = 'input'

    def updateWidgets(self):
        super(PhoneForm, self).updateWidgets()
        for name, widget in self.widgets.items():
            widget.addClass(name)

    def getContent(self):
        # Get the phone attribute from the contact
        if interfaces.IContact.providedBy(self.context):
            return getattr(self.context, self.attrName)
        # We are in the process of adding a contact, so store the phone
        # in a session variable.
        session = ISession(self.request)[SESSION_KEY]
        if self.attrName not in session:
            session[self.attrName] = contact.Phone()
        return session[self.attrName]

    @button.handler(form.AddForm.buttons['add'])
    def handleAdd(self, action):
        self.handleApply(self, action)

    @property
    def id(self):
        return (self.prefix + 'widgets.countryCode').replace('.', '-')

    @property
    def label(self):
        return interfaces.IContact[self.attrName].title

    @property
    def required(self):
        return interfaces.IContact[self.attrName].required


class PhonesForm(browser.BrowserPage):
    parentForm = None

    def update(self):
        self.prefix = self.parentForm.prefix + 'phones.'
        self.forms = []
        for name in ('homePhone', 'workPhone', 'cellPhone'):
            form = PhoneForm(self.context, self.request, self.parentForm)
            form.prefix = self.prefix + name + '.'
            form.attrName = name
            form.update()
            self.forms.append(form)

    def render(self):
        template = zope.component.getMultiAdapter(
            (self, self.request), IPageTemplate)
        return template(self)


class EMailForm(subform.EditSubForm, form.EditForm):
    form.extends(subform.EditSubForm)
    fields = field.Fields(interfaces.IEMail['fullAddress'])
    index = None
    deleted = False

    # In this application, we do not want this message
    noChangesMessage = None

    def updateWidgets(self):
        super(EMailForm, self).updateWidgets()
        for name, widget in self.widgets.items():
            widget.addClass(u'email')

    @button.handler(form.AddForm.buttons['add'])
    def handleAdd(self, action):
        self.handleApply(self, action)

    @button.buttonAndHandler(u'Delete')
    def handleDelete(self, action):
        emails = self.getContent().__parent__
        del emails[self.index]
        self.deleted = True


class EMailsForm(form.AddForm):
    fields = field.Fields(interfaces.IEMail['fullAddress'])
    parentForm = None

    def updateWidgets(self):
        super(EMailsForm, self).updateWidgets()
        for name, widget in self.widgets.items():
            widget.addClass(u'email')

    def create(self, data):
        address = contact.EMail(**data)
        return address

    def add(self, object):
        self.getContent().append(object)
        zope.location.locate(object, self.getContent())
        self.widgets.ignoreRequest = True
        self.widgets.update()
        return object

    def getContent(self):
        # Get the address container from the contact
        if interfaces.IContact.providedBy(self.context):
            return self.context.emails
        # We are in the process of adding a contact, so store the email list
        # in a session variable.
        session = ISession(self.request)[SESSION_KEY]
        if 'emails' not in session:
            session['emails'] = contact.EMails()
        return session['emails']

    def update(self):
        self.prefix = self.parentForm.prefix + 'emails.'
        super(EMailsForm, self).update()
        self.emailForms = []
        for index, email in enumerate(self.getContent()):
            form = EMailForm(email, self.request, self.parentForm)
            form.index = index
            form.prefix = self.prefix + str(index) + '.'
            form.update()
            if not form.deleted:
                self.emailForms.append(form)

    def render(self):
        template = zope.component.getMultiAdapter(
            (self, self.request), IPageTemplate)
        return template(self)


class ContactAddForm(form.AddForm):
    fields = field.Fields(interfaces.IContact).select(
        'firstName', 'lastName', 'birthday')
    fields['birthday'].widgetFactory = dateselect.DateSelectFieldWidget
    prefix = 'contact.add.'

    def update(self):
        self.updateWidgets()
        self.updateActions()

        self.addressesForm = AddressesForm(self.context, self.request)
        self.addressesForm.parentForm = self
        self.addressesForm.update()

        self.phonesForm = PhonesForm(self.context, self.request)
        self.phonesForm.parentForm = self
        self.phonesForm.update()

        self.emailsForm = EMailsForm(self.context, self.request)
        self.emailsForm.parentForm = self
        self.emailsForm.update()

        self.actions.execute()


    def create(self, data):
        newContact = contact.Contact(**data)

        newContact.addresses = self.addressesForm.getContent()
        zope.location.locate(newContact.addresses, newContact, 'addresses')
        del ISession(self.request)[SESSION_KEY]['addresses']

        for phoneForm in self.phonesForm.forms:
            phone = phoneForm.getContent()
            zope.location.locate(phone, newContact, phoneForm.attrName)
            setattr(newContact, phoneForm.attrName, phone)
            del ISession(self.request)[SESSION_KEY][phoneForm.attrName]

        newContact.emails = self.emailsForm.getContent()
        zope.location.locate(newContact.emails, newContact, 'emails')
        del ISession(self.request)[SESSION_KEY]['emails']

        return newContact


    def add(self, object):
        count = 0
        while 'contact-%i' %count in self.context:
            count += 1;
        self._name = 'contact-%i' %count
        self.context[self._name] = object
        return object


    def nextURL(self):
        return self.request.getURL()

AddContactLabel = button.StaticButtonActionAttribute(
    u'Add Contact', button=form.AddForm.buttons['add'], form=ContactAddForm)


class ContactEditForm(form.EditForm):
    form.extends(form.EditForm)
    fields = field.Fields(interfaces.IContact).select(
        'firstName', 'lastName', 'birthday')
    fields['birthday'].widgetFactory = dateselect.DateSelectFieldWidget
    prefix = 'contact.edit.'

    # In this application, we do not want this message
    noChangesMessage = None

    @button.buttonAndHandler(u'Delete')
    def handleDelete(self, action):
        # Delete the contact from the address book
        contact = self.getContent()
        addressbook = contact.__parent__
        del addressbook[contact.__name__]
        # Reset the selected item
        ISession(self.request)[SESSION_KEY]['selectedContact'] = None

    @button.buttonAndHandler(u'Done')
    def handleDone(self, action):
        # Reset the selected item
        ISession(self.request)[SESSION_KEY]['selectedContact'] = None

    def update(self):
        super(ContactEditForm, self).update()
        self.addressesForm = AddressesForm(self.context, self.request)
        self.addressesForm.parentForm = self
        self.addressesForm.update()

        self.phonesForm = PhonesForm(self.context, self.request)
        self.phonesForm.parentForm = self
        self.phonesForm.update()

        self.emailsForm = EMailsForm(self.context, self.request)
        self.emailsForm.parentForm = self
        self.emailsForm.update()


class SelectContactColumn(column.GetterColumn):
    zope.interface.implements(ISortableColumn)

    def renderCell(self, item, formatter):
        value = super(SelectContactColumn, self).renderCell(item, formatter)
        return '<a href="%s?selectContact=%s">%s</a>' %(
            formatter.request.getURL(), item.__name__, value)


class AddressBook(browser.BrowserPage):

    columns = (
        SelectContactColumn(
            u'Last Name', lambda i, f: i.lastName, name='lastName'),
        SelectContactColumn(
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
            self.form = ContactEditForm(self.selectedContact, self.request)
            self.form.update()
        if not self.selectedContact:
            self.form = ContactAddForm(self.context, self.request)
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
