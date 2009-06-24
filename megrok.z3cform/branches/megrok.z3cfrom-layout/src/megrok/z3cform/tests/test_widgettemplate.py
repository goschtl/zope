"""
  >>> manfred = Person()

  >>> from zope import component
  >>> from zope.interface import alsoProvides
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> alsoProvides(request, Skin)

  Check that fields have been created on the edition page:

  >>> view = component.getMultiAdapter((manfred, request), name='edit')
  >>> len(view.fields)
  2

  >>> [field.__name__ for field in view.fields.values()]
  ['name', 'age']

  >>> view.updateWidgets() 
  >>> print view.widgets['name'].render() 
  <input id="form-widgets-name" name="form.widgets.name"
         class="text-widget required textline-field"
         value="" type="text" /> 

  >>> view = component.getMultiAdapter((manfred, request), name='view')
  >>> view.updateWidgets() 
  >>> print view.widgets['name'].render()
  <span> Extra Widget </span>


  >>> view = component.getMultiAdapter((manfred, request), name='add')
  >>> view.updateWidgets() 
  >>> print view.widgets['name'].render()
  <span> Extra Widget </span>
"""

import grok
import megrok.layout

from zope import interface, schema
from zope.schema.fieldproperty import FieldProperty
from megrok import z3cform

from z3c.form import field, interfaces

class Skin(z3cform.FormLayer):
    grok.skin('skin')

grok.layer(Skin)


class IPerson(interface.Interface):
    name = schema.TextLine(title=u"Name")
    age = schema.Int(title=u"Age")


class Person(grok.Model):
    interface.implements(IPerson)

    name = FieldProperty(IPerson['name'])
    age = FieldProperty(IPerson['age'])


class MyLayout(megrok.layout.Layout):
    grok.context(Person)


class CustomStringTemplate(z3cform.WidgetTemplate):
    grok.context(Person)
    grok.template('new_string.pt')
    megrok.z3cform.directives.mode(interfaces.DISPLAY_MODE)

class Edit(z3cform.PageEditForm):
    grok.context(Person)
    fields = field.Fields(IPerson)

class View(z3cform.PageDisplayForm):
    grok.context(Person)
    fields = field.Fields(IPerson)

class Add(z3cform.PageAddForm):
    grok.context(Person)
    fields = field.Fields(IPerson)

class CustomTemplate(z3cform.WidgetTemplate):
    grok.name('custom_template')
    grok.context(Person)
    grok.template('custom_string.pt')
    megrok.z3cform.directives.view(interfaces.IAddForm)


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

