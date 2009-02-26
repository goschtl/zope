##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test Setup.

$Id$
"""
import zope.component
import zope.interface
from zope.traversing.testing import setUp as setupTraversing
from zope.traversing.interfaces import IContainmentRoot

import z3c.form.testing
from z3c.form.interfaces import IButtonAction
from z3c.form.testing import setupFormDefaults
from z3c.formext import component, form, converter

TestRequest = z3c.form.testing.TestRequest

def setupExtJSComponents():
    zope.component.provideAdapter(component.TextField)
    zope.component.provideAdapter(component.TextArea)
    zope.component.provideAdapter(component.DateField)
    zope.component.provideAdapter(component.FormPanel)
    zope.component.provideAdapter(component.ExtFormPanel)
    zope.component.provideAdapter(component.ComboBox)
    zope.component.provideAdapter(component.CheckBox)
    zope.component.provideAdapter(component.RadioGroup)
    zope.component.provideAdapter(component.Button)
    zope.component.provideAdapter(component.ClientButton)
    zope.component.provideAdapter(form.ClientButtonAction,
                                  provides=IButtonAction)

def setupFormExt():
    setupExtJSComponents()
    setupFormDefaults()
    setupTraversing()
    zope.component.provideAdapter(converter.ExtJSDateDataConverter)
    zope.component.provideAdapter(converter.ExtJSSingleCheckBoxDataConverter)


class Context(object):
    zope.interface.implements(IContainmentRoot)
    __name__ = ''

class TestingForm(object):

    __name__ = 'index.html'

    def getContent(self):
        if self.context is None:
            self.context = Context()
        return self.context
