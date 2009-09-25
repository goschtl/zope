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
