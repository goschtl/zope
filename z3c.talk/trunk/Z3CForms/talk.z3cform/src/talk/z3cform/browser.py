import datetime
from zope.app import pagetemplate
from zope.app import rotterdam
from zope.traversing.browser import absoluteURL
from z3c.form import button, field, form, widget
from z3c.form.interfaces import IAddForm, IFormLayer
from z3c.formui.interfaces import IDivFormLayer

from talk.z3cform import interfaces, message


class IFormSkin(IDivFormLayer, IFormLayer, rotterdam.Rotterdam):
    """Form Skin"""

DefaultDate = widget.ComputedWidgetAttribute(
    lambda adapter: datetime.date.today(),
    field=interfaces.IHelloWorldMessage['when'], view=IAddForm)

class HelloWorldAddForm(form.AddForm):
    label = u'Hello World Message Add Form'
    fields = field.Fields(interfaces.IHelloWorldMessage)
    template = pagetemplate.ViewPageTemplateFile('form.pt')

    def create(self, data):
        return message.HelloWorldMessage(**data)

    def add(self, object):
        count = 0
        while 'helloworld-%i' %count in self.context:
            count += 1;
        self._name = 'helloworld-%i' %count
        self.context[self._name] = object
        return object

    def nextURL(self):
        return absoluteURL(self.context[self._name], self.request)


class HelloWorldEditForm(form.EditForm):
    form.extends(form.EditForm)
    label = u'Hello World Message Edit Form'
    fields = field.Fields(interfaces.IHelloWorldMessage)
    template = pagetemplate.ViewPageTemplateFile('form.pt')

    @button.buttonAndHandler(u'Apply and View', name='applyView')
    def handleApplyView(self, action):
        self.handleApply(self, action)
        if not self.widgets.errors:
            url = absoluteURL(self.context, self.request)
            self.request.response.redirect(url)


class HelloWorldDisplayForm(form.DisplayForm):
    fields = field.Fields(interfaces.IHelloWorldMessage)
    template = pagetemplate.ViewPageTemplateFile('display.pt')

    def __call__(self):
        self.update()
        return self.render()
