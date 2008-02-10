__docformat__ = "reStructuredText"
import datetime

import zope.interface
from zope.schema import fieldproperty
from zope.traversing.browser import absoluteURL
from zope.app.folder.interfaces import IFolder

from z3c.form import button, field, form, widget
from z3c.form.interfaces import IAddForm
from z3c.formui import layout
from z3c.formdemo.message.interfaces import IHelloWorld

import grok

import mars.form
import mars.view
import mars.template
import mars.layer
import mars.adapter
from mars.formdemo.layer import IDemoBrowserLayer

mars.layer.layer(IDemoBrowserLayer)

class DefaultDate(mars.adapter.AdapterFactory):
    grok.name('default')
    mars.adapter.factory(widget.ComputedWidgetAttribute(
                        lambda adapter: datetime.date.today(),
                        field=IHelloWorld['when'], view=IAddForm))

class HelloWorld(grok.Model):
    """Content object"""
    zope.interface.implements(IHelloWorld)

    who = fieldproperty.FieldProperty(IHelloWorld['who'])
    when = fieldproperty.FieldProperty(IHelloWorld['when'])
    what = fieldproperty.FieldProperty(IHelloWorld['what'])

    def __init__(self, who, when, what):
        self.who = who
        self.when = when
        self.what = what

class Add(mars.form.FormView, layout.AddFormLayoutSupport, form.AddForm):
    """ A sample add form."""
    grok.name('addHelloWorld')
    grok.context(IFolder) # override the module-level context (HelloWorld)

    label = u'Hello World Message Add Form'
    fields = field.Fields(IHelloWorld)

    def create(self, data):
        return HelloWorld(**data)

    def add(self, object):
        count = 0
        while 'helloworld-%i' %count in self.context:
            count += 1;
        self._name = 'helloworld-%i' %count
        self.context[self._name] = object
        return object

    def nextURL(self):
        return absoluteURL(self.context[self._name], self.request)


class Edit(mars.form.FormView, layout.FormLayoutSupport, form.EditForm):
    grok.name('edit')
    form.extends(form.EditForm)
    label = u'Hello World Message Edit Form'
    fields = field.Fields(IHelloWorld)

    @button.buttonAndHandler(u'Apply and View', name='applyView')
    def handleApplyView(self, action):
        self.handleApply(self, action)
        if not self.widgets.errors:
            url = absoluteURL(self.context, self.request)
            self.request.response.redirect(url)


class Display(mars.form.FormView, layout.FormLayoutSupport, form.DisplayForm):
    grok.name('index')
    fields = field.Fields(IHelloWorld)

class DisplayTemplate(mars.template.LayoutFactory):
    grok.context(Display)
    grok.template('display.pt')

