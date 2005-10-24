##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Edit form directives

$Id$
"""
from zope.component import getMultiAdapter
from zope.app.form.browser.metaconfigure import BaseFormDirective

from zope.app.form.browser.metaconfigure import EditFormDirective as \
     zope_app_EditFormDirective
from zope.app.form.browser.metaconfigure import AddFormDirective as \
     zope_app_AddFormDirective

from zope.app.form.browser.editview import EditViewFactory as \
     zope_app_EditViewFactory
from zope.app.form.browser.add import AddViewFactory as \
     zope_app_AddViewFactory

from Products.Five.form import EditView, AddView
from Products.Five.security import protectClass, initializeClass
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

def EditViewFactory(name, schema, label, permission, layer,
                    template, default_template, bases, for_, fields,
                    fulledit_path=None, fulledit_label=None, menu=u''):
    zope_app_EditViewFactory(name, schema, label, permission, layer,
                             template, default_template, bases, for_, fields,
                             fulledit_path, fulledit_label)
    # fetch the class by looking up the adapter just registered
    class_ = getMultiAdapter((for_, layer), name=name)
    # patch in Zope 2 page templates
    class_.index = ZopeTwoPageTemplateFile(class_.index.filename)
    class_.generated_form = ZopeTwoPageTemplateFile(
        class_.generated_form.filename)
    # zope 2 security
    protectClass(class_, permission)
    initializeClass(class_)

class EditFormDirective(zope_app_EditFormDirective):

    view = EditView
    default_template = 'edit.pt'
    
    def __call__(self):
        self._processWidgets()
        self._handle_menu()
        self._context.action(
            discriminator=self._discriminator(),
            callable=EditViewFactory,
            args=self._args(),
        )

def AddViewFactory(name, schema, label, permission, layer,
                   template, default_template, bases, for_,
                   fields, content_factory, arguments,
                   keyword_arguments, set_before_add, set_after_add,
                   menu=u''):

    zope_add_AddViewFactory(name, schema, label, permission, layer,
                            template, default_template, bases, for_,
                            fields, content_factory, arguments,
                            keyword_arguments, set_before_add, set_after_add,
                            menu)
    # fetch adapter just registered
    class_ = getMultiAdapter((for_, layer), name=name)
    # monkey the zope 3 page template engine in
    class_.index = ZopeTwoPageTemplateFile(class_.index.filename)
    class_.generated_form = ZopeTwoPageTemplateFile(
        class_.generated_form.filename)
    # zope 2 security
    protectClass(class_, permission)
    initializeClass(class_)

class AddFormDirective(zope_app_AddFormDirective):
    view = AddView
    default_template = 'add.pt'
    
    def __call__(self):
        self._processWidgets()
        self._handle_menu()
        self._handle_content_factory()
        self._handle_arguments()

        self._context.action(
            discriminator=self._discriminator(),
            callable=AddViewFactory,
            args=self._args()+(self.content_factory, self.arguments,
                               self.keyword_arguments,
                               self.set_before_add, self.set_after_add),
            )
