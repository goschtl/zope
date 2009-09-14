# -*- coding: utf-8 -*-

import grokcore.viewlet
import zope.component as component
from megrok.z3cform.base import PageForm
from z3c.form.interfaces import ISubForm


class ComposedForm(PageForm):
    """A more generic form which can be composed of many others.
    """
    grokcore.viewlet.baseclass()

    template = grokcore.viewlet.PageTemplateFile('templates/composedform.pt')

    def updateSubForms(self):
        subforms = map(lambda x: x[1], component.getAdapters(
            (self.context, self.request,  self), ISubForm))
        subforms = grokcore.viewlet.util.sort_components(subforms)
        self.subforms = []
        # Update form
        for subform in subforms:
            if not subform.available():
                continue
            subform.update()
            subform.updateForm()
            self.subforms.append(subform)

    def updateForm(self):
        self.updateSubForms()
        super(PageForm, self).updateForm()
