# -*- coding: utf-8 -*-

import grokcore.view as grok
from megrok.z3cform.base import PageForm
from grokcore.view.meta.views import default_view_name
from z3c.form.interfaces import ISubForm


class SubForm(PageForm):
    """A form going in a composed form.
    """
    grok.baseclass()
    grok.implements(ISubForm)
    
    def __init__(self, context, request, parentForm=None):
        self.parentForm = self.__parent__ = parentForm
        super(PageForm, self).__init__(context, request)

    def available(self):
        return self.getContent() is not None

    @property
    def prefix(self):
        name = grok.name.bind().get(self) or default_view_name(self)
        return str('%s' % name)
