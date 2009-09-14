#!/usr/bin/python
# -*- coding: utf-8 -*-

import grokcore.viewlet as grok
from megrok.pagetemplate import PageTemplate
from megrok.z3cform.base.components import GrokForm

class SimpleForm(PageTemplate):
    grok.view(GrokForm)
