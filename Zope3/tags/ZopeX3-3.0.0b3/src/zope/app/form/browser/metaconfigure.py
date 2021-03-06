##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Configuration handlers for forms and widgets

$Id$
"""
import os

from zope.interface import implementedBy
from zope.configuration.exceptions import ConfigurationError

from zope.schema import getFieldNamesInOrder
from zope.app.container.interfaces import IAdding
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.publisher.browser.globalbrowsermenuservice import \
     menuItemDirective

from zope.app.form import CustomWidgetFactory
from add import AddView, AddViewFactory
from editview import EditView, EditViewFactory
from addwizard import AddWizardView, AddWizardViewFactory
from editwizard import EditWizardView, EditWizardViewFactory
from schemadisplay import DisplayView, DisplayViewFactory

class BaseFormDirective(object):

    # to be overriden by the subclasses
    view = None
    default_template = None

    # default basic information
    for_ = None
    layer = 'default'
    permission = 'zope.Public'
    template = None
    class_ = None

    # default form information
    title = None
    label = None
    menu = None
    fields = None

    def __init__(self, _context, **kwargs):
        self._context = _context
        for key, value in kwargs.items():
            if not (value is None and hasattr(self, key)):
                setattr(self, key, value)
        self._normalize()
        self._widgets = {}

    def widget(self, _context, field, class_, **kw):
        attrs = kw
        # Try to do better than accepting the string value by looking through
        # the interfaces and trying to find the field, so that we can use
        # 'fromUnicode()' 
        if isinstance(class_, type):
            ifaces = implementedBy(class_)
            for name, value in kw.items():
                for iface in ifaces:
                    if name in iface:
                        attrs[name] = iface[name].fromUnicode(value)
                        break
        self._widgets[field+'_widget'] = CustomWidgetFactory(class_, **attrs) 

    def _processWidgets(self):
        if self._widgets:
            customWidgetsObject = type('CustomWidgetsMixin', (object,),
                                       self._widgets) 
            self.bases = self.bases + (customWidgetsObject,)

    def _normalize(self):
        if self.for_ is None:
            self.for_ = self.schema

        if self.class_ is None:
            self.bases = (self.view,)
        else:
            self.bases = (self.class_, self.view)

        if self.template is not None:
            self.template = os.path.abspath(str(self.template))
            if not os.path.isfile(self.template):
                raise ConfigurationError("No such file", self.template)
        else:
            self.template = self.default_template

        self.names = getFieldNamesInOrder(self.schema)

        if self.fields:
            for name in self.fields:
                if name not in self.names:
                    raise ValueError("Field name is not in schema",
                                     name, self.schema)
        else:
            self.fields = self.names

    def _args(self):
        return (self.name, self.schema, self.label, self.permission,
                self.layer, self.template, self.default_template,
                self.bases, self.for_, self.fields)

    def _discriminator(self):
        return ('view', self.for_, self.name, IBrowserRequest,
                self.layer)


class Pane(object):
    ''' Holder for information about a Pane of a wizard '''
    # TODO: Add more funky stuff to each pane, such as a validator
    def __init__(self, field_names, label):
        self.names = field_names
        self.label = label


class BaseWizardDirective(BaseFormDirective):

    # default wizard information
    description = None
    use_session = False

    def __init__(self, _context, **kwargs):
        super(BaseWizardDirective, self).__init__(_context, **kwargs)
        self.panes = []

    def _args(self):
        return (self.name, self.schema, self.permission, self.layer,
                self.panes, self.fields, self.template, self.default_template,
                self.bases, self.for_)

    def pane(self, _context, fields, label=''):
        for f in fields:
            if f not in self.fields:
                raise ValueError(
                    'Field name is not in schema',
                    f, self.schema
                    )
        self.panes.append(Pane(fields, label))

class AddFormDirective(BaseFormDirective):

    view = AddView
    default_template = 'add.pt'
    for_ = IAdding

    # default add form information
    description = None
    content_factory = None
    arguments = None
    keyword_arguments = None
    set_before_add = None
    set_after_add = None

    def _handle_menu(self):
        if self.menu or self.title:
            if (not self.menu) or (not self.title):
                raise ValueError("If either menu or title are specified, "
                                 "they must both be specified")
            # Add forms are really for IAdding components, so do not use
            # for=self.schema.
            menuItemDirective(
                self._context, self.menu, self.for_, '@@' + self.name,
                self.title, permission=self.permission,
                description=self.description)

    def _handle_arguments(self, leftover=None):
        schema = self.schema
        fields = self.fields
        arguments = self.arguments
        keyword_arguments = self.keyword_arguments
        set_before_add = self.set_before_add
        set_after_add = self.set_after_add

        if leftover is None:
            leftover = fields

        if arguments:
            missing = [n for n in arguments if n not in fields]
            if missing:
                raise ValueError("Some arguments are not included in the form",
                                 missing)
            optional = [n for n in arguments if not schema[n].required]
            if optional:
                raise ValueError("Some arguments are optional, use"
                                 " keyword_arguments for them",
                                 optional)
            leftover = [n for n in leftover if n not in arguments]

        if keyword_arguments:
            missing = [n for n in keyword_arguments if n not in fields]
            if missing:
                raise ValueError(
                    "Some keyword_arguments are not included in the form",
                    missing)
            leftover = [n for n in leftover if n not in keyword_arguments]

        if set_before_add:
            missing = [n for n in set_before_add if n not in fields]
            if missing:
                raise ValueError(
                    "Some set_before_add are not included in the form",
                    missing)
            leftover = [n for n in leftover if n not in set_before_add]

        if set_after_add:
            missing = [n for n in set_after_add if n not in fields]
            if missing:
                raise ValueError(
                    "Some set_after_add are not included in the form",
                    missing)
            leftover = [n for n in leftover if n not in set_after_add]

            self.set_after_add += leftover

        else:
            self.set_after_add = leftover

    def __call__(self):
        self._processWidgets()
        self._handle_menu()
        self._handle_arguments()

        self._context.action(
            discriminator=self._discriminator(),
            callable=AddViewFactory,
            args=self._args()+(self.content_factory, self.arguments,
                                 self.keyword_arguments,
                                 self.set_before_add, self.set_after_add),
            kw={'menu': self.menu},
            )

class EditFormDirective(BaseFormDirective):

    view = EditView
    default_template = 'edit.pt'
    title = 'Edit'

    def _handle_menu(self):
        if self.menu:
            menuItemDirective(
                self._context, self.menu, self.for_ or self.schema,
                '@@' + self.name, self.title, permission=self.permission)

    def __call__(self):
        self._processWidgets()
        self._handle_menu()
        self._context.action(
            discriminator=self._discriminator(),
            callable=EditViewFactory,
            args=self._args(),
            kw={'menu': self.menu},
        )

class SubeditFormDirective(BaseFormDirective):

    view = EditView
    default_template = 'subedit.pt'

    # default subedit form directive
    fulledit_path = None
    fulledit_label = None

    def __call__(self):
        self._processWidgets()
        self._context.action(
            discriminator = self._discriminator(),
            callable = EditViewFactory,
            args = self._args()+(self.fulledit_path, self.fulledit_label),
            )

class AddWizardDirective(BaseWizardDirective, AddFormDirective):

    view = AddWizardView
    default_template = 'addwizard.pt'

    def __call__(self):
        self._handle_menu()

        all_fields = self.fields
        leftover = []
        for pane in self.panes:
            leftover.extend(pane.names)
        self.fields = leftover[:]
        self._handle_arguments(leftover)
        self.fields = all_fields

        self._context.action(
            discriminator = self._discriminator(),
            callable = AddWizardViewFactory,
            args = self._args()+(self.content_factory, self.arguments,
                                 self.keyword_arguments, self.set_before_add,
                                 self.set_after_add, self.use_session)
            )

class EditWizardDirective(BaseWizardDirective, EditFormDirective):

    view = EditWizardView
    default_template = 'editwizard.pt'

    def __call__(self):
        self._handle_menu()
        self._context.action(
            discriminator = self._discriminator(),
            callable = EditWizardViewFactory,
            args = self._args()+(self.menu, self.use_session)
            )

class SchemaDisplayDirective(EditFormDirective):

    view = DisplayView
    default_template = 'display.pt'

    def __call__(self):
        self._handle_menu()
        self._context.action(
            discriminator = self._discriminator(),
            callable = DisplayViewFactory,
            args = self._args()+(self.menu,)
            )
