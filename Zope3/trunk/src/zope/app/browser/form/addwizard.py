##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: addwizard.py,v 1.7 2003/08/03 02:13:02 philikon Exp $
"""

import sys
import logging

from zope.interface import implements, classProvides
from zope.schema.interfaces import ValidationError
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.interfaces.form import WidgetsError
from zope.app.form.utility import setUpWidgets, getWidgetsData
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.security.checker import defineChecker, NamesChecker
from zope.component import getAdapter
from zope.component.view import provideView
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.browser.form.submit import Update
from zope.app.browser.form.editview import EditView, normalize
from zope.app.publisher.browser.globalbrowsermenuservice \
     import menuItemDirective
from editwizard import EditWizardView, Pane, WizardStorage

class AddWizardView(EditWizardView):
    """Multi-page add-view base class.

    Subclasses should provide a schema attribute defining the schema
    to be edited.
    """

    def _setUpWidgets(self):
        if self.use_session:
            # Need session for File upload fields
            raise NotImplementedError, 'Need a working ISessionDataManager'
        else:
            self.storage = WizardStorage(self.fieldNames, None)

        setUpWidgets(self, self.schema, names=self.fieldNames)

    def create(self, *args, **kw):
        """Do the actual instantiation.
        """
        return self._factory(*args, **kw)

    def apply_update(self, data):
        """Add the desired object using the data in the data argument.

        The data argument is a dictionary with the data entered in the form.

        Issues a redirect to context.nextURL()

        Returns False, as per editview.apply_update
        """

        # This code originally from add.py's createAndAdd method
        
        args = []
        for name in self._arguments:
            args.append(data[name])

        kw = {}
        for name in self._keyword_arguments:
            if name in data:
                kw[str(name)] = data[name]

        content = self.create(*args, **kw)
        adapted = getAdapter(content, self.schema, context=self.context)

        errors = []

        for name in self._set_before_add:
            if name in data:
                field = self.schema[name]
                try:
                    field.set(adapted, data[name])
                except ValidationError:
                    errors.append(sys.exc_info()[1])

        if errors:
            raise WidgetsError(*errors)

        publish(self.context, ObjectCreatedEvent(content))

        content = self.context.add(content)

        adapted = getAdapter(content, self.schema)

        for name in self._set_after_add:
            if name in data:
                field = self.schema[name]
                try:
                    field.set(adapted, data[name])
                except ValidationError:
                    errors.append(sys.exc_info()[1])

        if errors:
            raise WidgetsError(*errors)

        self.request.response.redirect(self.context.nextURL())
        return False


def AddWizardViewFactory(
    name, schema, permission, layer, panes, fields,
    template, default_template, bases, for_, content_factory, arguments,
    keyword_arguments, set_before_add, set_after_add, use_session=True):

    class_  = SimpleViewClass(template, used_for = schema, bases = bases)

    class_.schema = schema
    class_.panes = panes
    class_.fieldNames = fields
    class_._factory = content_factory
    class_._arguments = arguments
    class_._keyword_arguments = keyword_arguments
    class_._set_before_add = set_before_add
    class_._set_after_add = set_after_add
    class_.use_session = use_session

    class_.generated_form = ViewPageTemplateFile(default_template)

    defineChecker(class_,
                  NamesChecker(
                    ("__call__", "__getitem__", "browserDefault"),
                    permission,
                    )
                  )

    provideView(for_, name, IBrowserPresentation, class_, layer)


class AddWizardDirective:

    def __init__(
        self, _context, name, schema, permission, content_factory='',
        layer='default', template=None, 
        for_='zope.app.interfaces.container.IAdding', class_=None, 
        arguments='',keyword_arguments='', set_before_add='', set_after_add='',
        menu=None, description='', title=None, use_session='yes'
        ):

        self.name = name
        self.permission = permission
        self.title = title
        self.layer = layer
        self.menu = menu
        self.set_before_add = set_before_add
        self.set_after_add = set_after_add

        if use_session == 'yes':
            self.use_session = True
        elif use_session == 'no':
            self.use_session = False
        else:
            raise ValueError('Invalid value %r for use_session'%(use_session,))

        # Handle menu attrs. We do this now to rather than later becaise
        # menuItemDirective expects a dotted name for for_. 
        if menu or title:
            if (not menu) or (not title):
                raise ValueError("If either menu or title are specified, "
                                "they must both be specified")
            menuItemDirective(
                _context, menu, for_, '@@' + name, title,
                permission=permission, description=description)

        self.content_factory = content_factory

        for_, bases, template, fields = normalize(
            for_, schema, class_, template, 'addwizard.pt', view=AddWizardView)

        self._context = _context
        self.schema = schema
        self.for_ = for_
        self.bases = bases
        self.template = template
        self.all_fields = fields

        self.arguments = arguments
        self.keyword_arguments = keyword_arguments
 
        self.panes = []

    def pane(self, _context, fields, label=''):
        for f in fields:
            if f not in self.all_fields:
                raise ValueError(
                    'Field name is not in schema', 
                    name, self.schema
                    )
        self.panes.append(Pane(fields, label))

    def __call__(self):

        # Argument code Cut & Paste from add.py
        leftover = []
        for pane in self.panes:
            leftover.extend(pane.names)
        fields = leftover[:]

        arguments = self.arguments
        if arguments:
            missing = [n for n in arguments if n not in fields]
            if missing:
                raise ValueError("Some arguments are not included in the form",
                                missing)
            optional = [n for n in arguments if not self.schema[n].required]
            if optional:
                raise ValueError("Some arguments are optional, use"
                                " keyword_arguments for them",
                                optional)
            leftover = [n for n in leftover if n not in arguments]

        keyword_arguments = self.keyword_arguments
        if keyword_arguments:
            missing = [n for n in keyword_arguments if n not in fields]
            if missing:
                raise ValueError(
                    "Some keyword_arguments are not included in the form",
                    missing)
            leftover = [n for n in leftover if n not in keyword_arguments]

        set_before_add = self.set_before_add
        if set_before_add:
            missing = [n for n in set_before_add if n not in fields]
            if missing:
                raise ValueError(
                    "Some set_before_add are not included in the form",
                    missing)
            leftover = [n for n in leftover if n not in set_before_add]

        set_after_add = self.set_after_add
        if set_after_add:
            missing = [n for n in set_after_add if n not in fields]
            if missing:
                raise ValueError(
                    "Some set_after_add are not included in the form",
                    missing)
            leftover = [n for n in leftover if n not in set_after_add]

            set_after_add += leftover

        else:

            set_after_add = leftover

        self._context.action(
            discriminator=('view', self.for_, self.name, IBrowserPresentation, 
                           self.layer),
            callable=AddWizardViewFactory,
            args=(self.name, self.schema, self.permission, self.layer, 
                  self.panes, self.all_fields, self.template, 'editwizard.pt',
                  self.bases, self.for_, self.content_factory, arguments,
                  keyword_arguments, self.set_before_add, self.set_after_add,
                  self.use_session)
            )
