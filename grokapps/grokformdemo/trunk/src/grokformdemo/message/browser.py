import grok
import megrok.z3cform.base

#
import message
import interfaces
import datetime

#
from z3c.form import field, form, button, widget
from grokformdemo.app import Grokformdemo
from grokformdemo.ajax import mytooltip 
from grokcore.component import global_adapter
from z3c.form.interfaces import IAddForm

DefaultDate = widget.ComputedWidgetAttribute(
    lambda adapter: datetime.date.today(),
    field=interfaces.IHelloWorld['when'], view=IAddForm)

global_adapter(DefaultDate, name='default')




class HelloWorldAddForm(megrok.z3cform.base.PageAddForm):
    """ A sample add form."""
    grok.context(Grokformdemo)

    label = u'Hello World Message Add Form'
    fields = field.Fields(interfaces.IHelloWorld)

    def update(self):
        mytooltip.need()

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
	return self.redirect(self.url(self.context[self._name]))

class HelloWorldEditForm(megrok.z3cform.base.PageEditForm):
    grok.context(message.HelloWorld)
    grok.name('edit.html')
    form.extends(form.EditForm)
    label = u'Hello World Message Edit Form'
    fields = field.Fields(interfaces.IHelloWorld)

    def update(self):
        mytooltip.need()

    @button.buttonAndHandler(u'Apply and View', name='applyView')
    def handleApplyView(self, action):
        self.handleApply(self, action)
        if not self.widgets.errors:
	    self.redirect(self.url(self.context, name='index'))


class HelloWorldDisplayForm(megrok.z3cform.base.PageDisplayForm):
    """ A simple Display Form"""
    grok.context(message.HelloWorld)
    grok.name('index')
    template = grok.PageTemplateFile('display.pt')

    fields = field.Fields(interfaces.IHelloWorld)
