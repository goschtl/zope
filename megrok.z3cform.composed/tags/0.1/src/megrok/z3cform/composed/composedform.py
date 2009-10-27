# -*- coding: utf-8 -*-

import grokcore.viewlet as grok
import zope.component as component
import megrok.pagetemplate as pt
from megrok.z3cform.base import PageForm
from z3c.form.interfaces import ISubForm

grok.templatedir("templates")

class ComposedForm(PageForm):
    """A more generic form which can be composed of many others.
    """
    grok.baseclass()
    subforms = []

    def updateSubForms(self):
        subforms = map(lambda x: x[1], component.getAdapters(
            (self.context, self.request,  self), ISubForm))
        subforms = grok.util.sort_components(subforms)
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


class ComposedTemplate(pt.PageTemplate):
    """A template rendering a composed form.
    """
    grok.view(ComposedForm)
