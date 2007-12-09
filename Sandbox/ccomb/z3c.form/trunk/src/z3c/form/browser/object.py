__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces

from z3c.form import interfaces
from z3c.form.widget import Widget, FieldWidget
from z3c.form.field import FieldWidgets, Fields
from z3c.form.browser import widget
from z3c.form.subform import EditSubForm

# FIXME: see if there is some interesting specific attributes for <fieldset>
# We should then create a HTMLFieldsetElement and use it instead of base HTMLFormElement

# FIXME where and when does the object creation takes place?

class ObjectWidget(widget.HTMLFormElement, Widget):
    zope.interface.implementsOnly(interfaces.IObjectWidget)

    klass = u'object-widget'
    widgets = None

    def update(self):
        if interfaces.IFormAware.providedBy(self) \
                                        and not hasattr(self.form, self.name):
            #FIXME None for add form, widget.context.? for editform
            #FIXME: use a factory to create the subform, to be able
            # to derive it from things like AddFormLayoutSupport
            subform = EditSubForm(None, self.request, self.form)
            subform.fields = Fields(self.field.schema)
            setattr(self.form, self.field.__name__, subform)
            zope.interface.alsoProvides(self, interfaces.ISubformAware)
            self.subform = subform
        if interfaces.ISubformAware.providedBy(self):
            self.subform.update()
        super(ObjectWidget, self).update()
    def render(self):
        return super(ObjectWidget, self).render()
    def extract(self, default=interfaces.NOVALUE):
        extracted = self.subform.widgets.extract()
        return extracted

@zope.component.adapter(zope.schema.interfaces.IObject, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def ObjectFieldWidget(field, request):
    """IFieldWidget factory for IObjectWidget."""
    return FieldWidget(field, ObjectWidget(request))

