# -*- coding: utf-8 -*-

from z3c.form.interfaces import IButtonForm, IHandlerForm


class IGrokForm(IButtonForm, IHandlerForm):
    """A grok z3c form. This marker interface is used to have a
    different default template.
    """
