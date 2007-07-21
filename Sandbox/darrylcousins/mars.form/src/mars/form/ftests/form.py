"""

  >>> import grok
  >>> grok.grok('mars.form.ftests.form')
  >>> root = getRootFolder()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

These tests make use of minimal layer

  >>> skinURL = 'http://localhost/++skin++formskin'
  >>> browser.open(skinURL + '/add')

If we submit the form by clicking on add, ...

  >>> browser.getControl('Add').click()

... the same page returns telling us we have some errors:

This is because we forgot to enter the "Who" field, which is required:

  >>> print browser.contents
  <html>
  ...
  <div class="summary">There were some errors.</div>
  ...
  <li>
     Who: <div class="error">Required input is missing.</div>
  </li>
  ...
  </html>

Let's now fill out all the required fields and try to add the message again:

  >>> browser.getControl('Who').value = u'Manfred'
  >>> browser.getControl('Add').click()
  >>> print browser.url
  http://localhost/++skin++formskin/manfred

  >>> print browser.contents
  <div>
  <span id="form-widgets-when" class="textWidget date-field">
  ...
  </span>
  <span id="form-widgets-who"
        class="textWidget textline-field">
    Manfred
  </span>
  </div>

The default value for when should have rendered today.

  >>> import datetime
  >>> root['manfred'].when == datetime.date.today()
  True

We can also edit manfred with the edit form.

  >>> browser.open(skinURL + '/manfred/edit')

Let us now change the date and the name to test the form.

  >>> browser.getControl('Who').value = u'Manfred the man'
  >>> browser.getControl('When').value = u'08/08/20'
  >>> browser.getControl('Apply and View').click()
  >>> print browser.url
  http://localhost/++skin++formskin/manfred

  >>> print browser.contents
  <div>
  <span id="form-widgets-when" class="textWidget date-field">
  08/08/20
  </span>
  <span id="form-widgets-who"
        class="textWidget textline-field">
    Manfred the man
  </span>
  </div>

"""
import datetime

import zope.interface
import zope.schema
from zope.schema import fieldproperty
from zope.traversing.browser import absoluteURL
from zope.app.folder.interfaces import IFolder
from zope.publisher.interfaces.browser import IBrowserPage

from z3c.form import form, field, widget, button
from z3c.form.interfaces import IAddForm
from z3c.formui import layout

import grok

import mars.view
import mars.template
import mars.layer
import mars.adapter

## set up the layer, skin and template
class IMyFormLayer(mars.form.IDivFormLayer):
    pass

mars.layer.layer(IMyFormLayer)

class FormSkin(mars.layer.Skin):
    pass

class Template(mars.template.LayoutFactory):
    """main template for pages (note the context!)"""
    grok.context(IBrowserPage)
    grok.template('template.pt')

class IMessage(zope.interface.Interface):

    who = zope.schema.TextLine(
        title=u'Who',
        description=u'Name of the person sending the message',
        required=True)

    when = zope.schema.Date(
        title=u'When',
        description=u'Date of the message sent.',
        required=True)

class Message(grok.Model):
    """Content object"""
    zope.interface.implements(IMessage)

    who = fieldproperty.FieldProperty(IMessage['who'])
    when = fieldproperty.FieldProperty(IMessage['when'])

    def __init__(self, who, when):
        self.who = who
        self.when = when

class Edit(mars.form.FormView, layout.FormLayoutSupport, form.EditForm):
    form.extends(form.EditForm)
    label = u'Message Edit Form'
    fields = field.Fields(IMessage)

    @button.buttonAndHandler(u'Apply and View', name='applyView')
    def handleApplyView(self, action):
        self.handleApply(self, action)
        if not self.widgets.errors:
            url = absoluteURL(self.context, self.request)
            self.request.response.redirect(url)

class DefaultDate(mars.adapter.AdapterFactory):
    """Create a default date adapter for the `when` field"""
    grok.name('default')
    mars.adapter.factory(widget.ComputedWidgetAttribute(
                        lambda adapter: datetime.date.today(),
                        field=IMessage['when'], view=IAddForm))

class Add(mars.form.FormView, layout.AddFormLayoutSupport, form.AddForm):
    grok.context(IFolder) #

    label = u'Message Add Form'
    fields = field.Fields(IMessage)

    def create(self, data):
        return Message(**data)

    def add(self, object):
        name = object.who.lower()
        self._name = name
        self.context[name] = object
        return object

    def nextURL(self):
        return absoluteURL(self.context[self._name], self.request)

class Display(mars.form.FormView, layout.FormLayoutSupport, form.DisplayForm):
    grok.name('index')
    fields = field.Fields(IMessage)

class DisplayTemplate(mars.template.LayoutFactory):
    grok.context(Display)
    grok.template('display.pt')

