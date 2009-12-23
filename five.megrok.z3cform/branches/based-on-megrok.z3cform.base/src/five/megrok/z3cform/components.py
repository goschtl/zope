import Acquisition
import martian
from megrok.z3cform.base import components
from plone.z3cform import z2

from z3c.form import form
from z3c.form.interfaces import IFormLayer


class GrokForm(components.GrokForm):

    def __init__(self, *args):
        super(GrokForm, self).__init__(*args)
        if not (self.static is None):
            self.static = self.static.__of__(self)

    getPhysicalPath = Acquisition.Acquired

    def __call__(self):
        """Render the form, patching the request first with
        plone.z3cform helper.
        """
        z2.switch_on(self, request_layer=IFormLayer)
        return super(GrokForm, self).__call__()


class Form(GrokForm, form.Form):

    martian.baseclass()

    def update(self):
        form.Form.update(self)


class AddForm(GrokForm, form.AddForm):

    martian.baseclass()

    def update(self):
        form.AddForm.update(self)


class EditForm(GrokForm, form.EditForm):

    martian.baseclass()

    def update(self):
        form.EditForm.update(self)


class DisplayForm(GrokForm, form.DisplayForm):

    martian.baseclass()

    def update(self):
        form.Form.update(self)

import five.grok
import z3c.form
from Acquisition import aq_inner


class FormView(five.grok.View):

    request_layer = z3c.form.interfaces.IFormLayer

    def __init__(self, context, request):
        super(FormView, self).__init__(context, request)
        self.form = self.formClass(
            aq_inner(self.context), self.request)
        self.form.__name__ = self.__name__

    def update(self):
        """On update, we switch on the zope3 request, needed to work with
        our z3c form. We update here the wrapped form.

        Override this method if you have more than one form.
        """
        z2.switch_on(self, request_layer=self.request_layer)
        self.form.update()
