import zc.ajax.application
import zc.ajax.form
import zope.formlib
import zope.interface
import zope.schema

class IPerson(zope.interface.Interface):

    first_name = zope.schema.TextLine(
        title = u"First name",
        description = u"Given name.",
        )

    last_name = zope.schema.TextLine(
        title = u"Last name",
        description = u"Family name.",
        )

    favorite_color = zope.schema.TextLine(
        title = u"Favorite color",
        required = False,
        )

    age = zope.schema.Int(
        title = u"Age",
        description = u"Age in years",
        min = 0,
        )

class Person:

    zope.interface.implements(IPerson)

    def __init__(self, first_name, last_name, favorite_color, age):
        self.first_name = first_name
        self.last_name = last_name
        self.favorite_color = favorite_color
        self.age = age

class FormExample(zc.ajax.application.Application):

    resource_library_name = None

    class ExampleForm(zc.ajax.form.Form):

        form_fields = zope.formlib.form.Fields(IPerson)

        @zope.formlib.form.action("Register")
        def register(self, action, data):
            return dict(
                data = data,
                self_class_name = self.__class__.__name__,
                self_app_class_name = self.app.__class__.__name__,
                self_context_class_name = self.context.__class__.__name__
                )
