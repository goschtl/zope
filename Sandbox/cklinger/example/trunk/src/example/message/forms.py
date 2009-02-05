import grok
import datetime
from zope.traversing.browser import absoluteURL
from z3c.form import button, field, form, widget
from z3c.form.interfaces import IAddForm

import interfaces, message
from megrok.z3cform import AddForm, EditForm, DisplayForm
from example.app import MySkin
from example.app import Example
from zope.interface import Interface
import megrok.pagelet

grok.layer(MySkin)


class HelloWorldAddForm(AddForm):
    """ A sample add form."""
    grok.context(Example)
    fields = field.Fields(interfaces.IHelloWorld)

    def create(self, data):
        return message.HelloWorld(**data)

    def add(self, object):
        count = 0
        while 'helloworld-%i' %count in self.context:
            count += 1;
        self._name = 'helloworld-%i' %count
        self.context[self._name] = object
        return object

    def nextURL(self):
        return absoluteURL(self.context[self._name], self.request)


class HelloWorldEditForm(EditForm):
    grok.context(message.HelloWorld)
    form.extends(form.EditForm)
    label = u'Hello World Message Edit Form'
    fields = field.Fields(interfaces.IHelloWorld)

    @button.buttonAndHandler(u'Apply and View', name='applyView')
    def handleApplyView(self, action):
        self.handleApply(self, action)
        if not self.widgets.errors:
            url = absoluteURL(self.context, self.request)
            self.request.response.redirect(url)

class HelloWorldDisplayForm(DisplayForm):
    grok.context(message.HelloWorld)
    grok.name('index')
    fields = field.Fields(interfaces.IHelloWorld)


class NewLayout(megrok.pagelet.LayoutView):
    grok.context(message.HelloWorld)
    megrok.pagelet.template('otherlayout.pt')
