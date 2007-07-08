__docformat__ = "reStructuredText"
import zope.interface
import zope.schema
import zope.annotation
from zope.schema import fieldproperty
from zope.traversing.browser import absoluteURL
from zope.app.folder.interfaces import IFolder
from zope.viewlet.viewlet import CSSViewlet

from z3c.form import form, field
from z3c.form.interfaces import IWidgets
from z3c.form.interfaces import HIDDEN_MODE
from z3c.template.interfaces import ILayoutTemplate
from z3c.formdemo.widgets.interfaces import IAllFields

import grok

import mars.view
import mars.template
import mars.layer
import mars.adapter
import mars.resource
from mars.formdemo.layer import IDemoBrowserLayer
from mars.formdemo.skin import skin

mars.layer.layer(IDemoBrowserLayer)

class AllFields(grok.Model):

    zope.interface.implements(IAllFields)
    zope.component.adapts(zope.annotation.interfaces.IAttributeAnnotatable)

    asciiField = fieldproperty.FieldProperty(IAllFields['asciiField'])
    asciiLineField = fieldproperty.FieldProperty(IAllFields['asciiLineField'])
    boolField = fieldproperty.FieldProperty(IAllFields['boolField'])
    bytesField = fieldproperty.FieldProperty(IAllFields['bytesField'])
    bytesLineField = fieldproperty.FieldProperty(IAllFields['bytesLineField'])
    choiceField = fieldproperty.FieldProperty(IAllFields['choiceField'])
    optionalChoiceField = fieldproperty.FieldProperty(
        IAllFields['optionalChoiceField'])
    promptChoiceField = fieldproperty.FieldProperty(
        IAllFields['promptChoiceField'])
    dateField = fieldproperty.FieldProperty(IAllFields['dateField'])
    datetimeField = fieldproperty.FieldProperty(IAllFields['datetimeField'])
    decimalField = fieldproperty.FieldProperty(IAllFields['decimalField'])
    dictField = fieldproperty.FieldProperty(IAllFields['dictField'])
    dottedNameField = fieldproperty.FieldProperty(IAllFields['dottedNameField'])
    floatField = fieldproperty.FieldProperty(IAllFields['floatField'])
    frozenSetField = fieldproperty.FieldProperty(IAllFields['frozenSetField'])
    idField = fieldproperty.FieldProperty(IAllFields['idField'])
    intField = fieldproperty.FieldProperty(IAllFields['intField'])
    listField = fieldproperty.FieldProperty(IAllFields['listField'])
    objectField = fieldproperty.FieldProperty(IAllFields['objectField'])
    passwordField = fieldproperty.FieldProperty(IAllFields['passwordField'])
    setField = fieldproperty.FieldProperty(IAllFields['setField'])
    sourceTextField = fieldproperty.FieldProperty(IAllFields['sourceTextField'])
    textField = fieldproperty.FieldProperty(IAllFields['textField'])
    textLineField = fieldproperty.FieldProperty(IAllFields['textLineField'])
    timeField = fieldproperty.FieldProperty(IAllFields['timeField'])
    timedeltaField = fieldproperty.FieldProperty(IAllFields['timedeltaField'])
    tupleField = fieldproperty.FieldProperty(IAllFields['tupleField'])
    uriField = fieldproperty.FieldProperty(IAllFields['uriField'])
    hiddenField = fieldproperty.FieldProperty(IAllFields['hiddenField'])

# register the AllField class as a annotation adapter
zope.component.provideAdapter(zope.annotation.factory(AllFields))

#  fix me: this adapter factory fails because although the annotation factory
# returns a `bound` method, when the factory is registered in the grokker it
# appears as an `unbound` method and therefore fails when it is called
# Is this something happening in martian????
#class GetAllFields(mars.adapter.AdapterFactory):
#    mars.adapter.factory(zope.annotation.factory(AllFields))

class AllFieldsForm(mars.view.PageletView, form.EditForm):
    """A form showing all fields."""
    grok.name('widgets')
    grok.context(zope.interface.Interface)
    fields = field.Fields(IAllFields).omit(
        'dictField', 'objectField')
    label = 'Widgets Demo'

    def getContent(self):
        return IAllFields(self.context)

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.update()
        self.widgets['hiddenField'].mode = HIDDEN_MODE
        self.widgets['promptChoiceField'].prompt = True
        self.widgets['promptChoiceField'].update()

    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)

