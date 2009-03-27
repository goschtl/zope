##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Representation of Form view classes.

$Id$
"""
import os
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from z3c.builder.core import base, interfaces, python

class AddFormBuilder(python.ModuleBuilderGetter, base.ContentBuilder):
    zope.interface.implements(interfaces.IAddFormBuilder)

    interface = FieldProperty(interfaces.IAddFormBuilder['interface'])
    factory = FieldProperty(interfaces.IAddFormBuilder['factory'])
    fields = FieldProperty(interfaces.IAddFormBuilder['fields'])
    next = FieldProperty(interfaces.IAddFormBuilder['next'])
    label = FieldProperty(interfaces.IAddFormBuilder['label'])

    def __init__(self, name, interface, factory,
                 fields=(), next='index.html', label=u'Add Form'):
        super(AddFormBuilder, self).__init__(name)
        self.interface = interface
        self.factory = factory
        self.fields = tuple([str(f) for f in fields])
        self.next = next
        self.label = label

    def update(self):
        """See interfaces.IBaseBuilder"""
        self.getModuleBuilder().imports += [
            'z3c.form.form.AddForm',
            'z3c.form.field.Fields',
            'zope.traversing.browser.absoluteURL',
            self.interface,
            self.factory]

    def render(self):
        """See interfaces.IContentBuilder"""
        template = open(base.getTemplatePath('add-form.py'), 'r').read()
        output = (template %{
            'interface': self.interface.rsplit('.', 1)[-1],
            'label': self.label,
            'fields': ', '.join([repr(field) for field in self.fields]),
            'factory': self.factory.rsplit('.', 1)[-1],
            'next': self.next,
            'className':self.name,
            })
        output += '\n'
        return output


class EditFormBuilder(python.ModuleBuilderGetter, base.ContentBuilder):
    zope.interface.implements(interfaces.IEditFormBuilder)

    interface = FieldProperty(interfaces.IEditFormBuilder['interface'])
    fields = FieldProperty(interfaces.IEditFormBuilder['fields'])
    label = FieldProperty(interfaces.IEditFormBuilder['label'])

    def __init__(self, name, interface, fields=(), label=u'Edit Form'):
        super(EditFormBuilder, self).__init__(name)
        self.interface = interface
        self.fields = tuple([str(f) for f in fields])
        self.label = label

    def update(self):
        self.getModuleBuilder().imports += [
            'z3c.form.form.EditForm',
            'z3c.form.field.Fields',
            self.interface]

    def render(self):
        template = open(base.getTemplatePath('edit-form.py'), 'r').read()
        output = (template %{
            'interface': self.interface.rsplit('.', 1)[-1],
            'label': self.label,
            'fields': ', '.join([repr(field) for field in self.fields]),
            'className':self.name,
            })
        output += '\n'
        return output


class SimpleDisplayFormBuilder(python.ModuleBuilderGetter, base.ContentBuilder):
    zope.interface.implements(interfaces.IDisplayFormBuilder)

    interface = FieldProperty(interfaces.IDisplayFormBuilder['interface'])
    fields = FieldProperty(interfaces.IDisplayFormBuilder['fields'])
    template = FieldProperty(interfaces.IDisplayFormBuilder['template'])

    def __init__(self, name, interface, template=None, fields=()):
        super(SimpleDisplayFormBuilder, self).__init__(name)
        self.interface = interface
        self.template = template
        self.fields = tuple([str(f) for f in fields])

    def update(self):
        self.getModuleBuilder().imports += [
            'z3c.form.form.Form',
            'z3c.form.form.DisplayForm',
            'z3c.form.field.Fields',
            self.interface]
        # Add the template for the form.
        if self.template:
            browserPackage = self.getModuleBuilder().__parent__
            if 'display.pt' not in browserPackage:
                zpt = base.SimpleFileBuilder(
                    u'display.pt', base.getTemplatePath('simple-display-form.pt'))
                browserPackage.add(zpt)
                zpt.update()

    def render(self):
        template = open(
            base.getTemplatePath('simple-display-form.py'), 'r').read()
        output = (template %{
            'interface': self.interface.rsplit('.', 1)[-1],
            'fields': ', '.join([repr(field) for field in self.fields]),
            'template': self.template,
            'className': self.name,
            })
        output += '\n'
        return output
