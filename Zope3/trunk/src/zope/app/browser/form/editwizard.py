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
$Id: editwizard.py,v 1.7 2003/07/28 22:20:58 jim Exp $
"""

import logging
from UserDict import UserDict
from zope.interface import implements, classProvides
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.component import getAdapter
from zope.app.publisher.browser.globalbrowsermenuservice \
     import menuItemDirective, globalBrowserMenuService
from zope.configuration.action import Action
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from editview import normalize, EditViewFactory, EditView
from zope.security.checker import defineChecker, NamesChecker
from zope.app.context import ContextWrapper
from zope.component.view import provideView
from zope.app.form.utility \
        import setUpEditWidgets, getWidgetsData, applyWidgetsChanges
from zope.app.interfaces.form import WidgetInputError
from submit import Next, Previous, Update
from zope.app.interfaces.form import WidgetsError
from zope.i18n import MessageIDFactory
from zope.app.event import publish
from zope.app.event.objectevent import ObjectModifiedEvent

PaneNumber = 'CURRENT_PANE_IDX'

# TODO: Needs to be persistent aware for session (?)
class WizardStorage(dict):
    def __init__(self, fields, content):
        super(WizardStorage, self).__init__(self)
        if content:
            for k in fields:
                self[k] = getattr(content,k)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError, key

    def __setattr__(self, key, value):
        self[key] = value


class EditWizardView(EditView):

    def _setUpWidgets(self):
        adapted = getAdapter(self.context, self.schema)
        if adapted is not self.context:
            adapted = ContextWrapper(adapted, self.context, name='(adapted)')
        self.adapted = adapted

        if self.use_session:
            # Need session for File upload fields
            raise NotImplementedError, \
                'Cannot be implemented until we have an ISessionDataManager'
        else:
            self.storage = WizardStorage(self.fieldNames, adapted)

        # Add all our widgets as attributes on this view
        setUpEditWidgets(
            self, self.schema, names=self.fieldNames, content=self.storage
            )

    def widgets(self):
        return [getattr(self, name+'_widget') 
            for name in self.currentPane().names
            ]

    _current_pane_idx = 0

    def currentPane(self):
        return self.panes[self._current_pane_idx]

    _update_called = 0

    # Message rendered at the top of the form, probably set by update()
    feedback = u'' 

    def update(self):
        '''
        Called before rendering each pane. It is responsible
        for extracting data into temporary storage, and selecting
        which pane should be rendered.
        '''
        # Calling twice does nothing
        if self._update_called:
            return
        self._update_called = 1

        # Determine the current pane
        if PaneNumber in self.request:
            self._current_pane_idx = int(self.request[PaneNumber])
            assert self._current_pane_idx >= 0
            assert self._current_pane_idx < len(self.panes)
        else:
            # First page
            self._current_pane_idx = 0
            self.errors = {}
            self.label = self.currentPane().label
            self._choose_buttons()
            return

        # Validate the current pane, and set self.errors
        try:
            if self.use_session:
                names = self.currentPane().names
            else:
                names = self.fieldNames
            data = getWidgetsData(
                self, self.schema, strict=True, set_missing=True, 
                names=names, exclude_readonly=True
                )
            self.errors = {}
        except WidgetsError, errors:
            errors = {}
            for k, label, msg in errors:
                errors[k] = msg
            self.errors = errors

        else:
            self.storage.update(data)

            if Next in self.request:
                self._current_pane_idx += 1
                assert self._current_pane_idx < len(self.panes)
            elif Previous in self.request:
                self._current_pane_idx -= 1
                assert self._current_pane_idx >= 0
            elif Update in self.request:
                if self.apply_update(self.storage):
                    self.feedback = _(u'No changes to save')
                else:
                    self.feedback = _(u'Changes saved')

        # Set the current label
        self.label = self.currentPane().label

        self._choose_buttons()

    def _choose_buttons(self):
        '''Determine what buttons appear when we render the current pane'''

        # The submit button appears if every field on every pane except the
        # current one has valid input or a valid default value.
        # This is almost always the case for edit forms.
        try:
            for k in self.fieldNames:
                if k not in self.currentPane().names:
                    debug = getattr(self, k).getData(1)
            self.show_submit = 1 
        except WidgetInputError,x:
            self.show_submit = 0

        self.show_next = (self._current_pane_idx < len(self.panes) - 1)

        self.show_previous = self._current_pane_idx > 0

    def apply_update(self, storage):
        ''' Save changes to our content object '''
        for k,v in storage.items():
            getattr(self,k).setData(v)
        content = self.adapted
        changed = applyWidgetsChanges(
                self, content, self.schema,
                names=self.fieldNames, exclude_readonly=True
                )
        # We should not generate events when an adapter is used.
        # That's the adapter's job
        if changed and self.context is self.adapted:
            publish(content, ObjectModifiedEvent(content))
        return not changed

    def renderHidden(self):
        ''' Render state as hidden fields. Also render hidden fields to 
            propagate self.storage if we are not using the session to do this.
        '''
        olist = []
        out = olist.append

        # the index of the pane being rendered needs to be propagated
        out('<input class="hiddenType" type="hidden" name="%s" value="%d" />'%(
            PaneNumber, self._current_pane_idx
            ))

        if self.use_session:
            # Need to output a unique key as a hidden field to identity this 
            # particular wizard. We use this to ensure data for this view 
            # doesn't conflict with other wizards in progress in other 
            # browser windows.
            # Otherwise, no more state to propagate
            raise NotImplementedError, 'use_session'

        else:
            current_fields = self.currentPane().names
            for k in self.fieldNames:
                if k not in current_fields:
                    widget = getattr(self, k)
                    out(widget.hidden())
            return ''.join(olist)


class Pane:
    # TODO: Add more funky stuff to each pane, such as a validator
    def __init__(self, field_names, label):
        self.names = field_names
        self.label = label


class EditWizardDirective:

    def __init__(self, _context, name, schema, permission, 
                 for_=None, class_=None, template=None, layer='default',
                 menu=None, title='Edit', use_session='yes'):
        self.name = name
        self.permission = permission
        self.title = title
        self.layer = layer
        self.menu = menu

        if use_session.lower() == 'yes':
            self.use_session = True
        elif use_session.lower() == 'no':
            self.use_session = False
        else:
            raise ValueError('Invalid value %r for use_session'%(use_session,))

        if menu:
            actions = menuItemDirective(
                _context, menu, for_ or schema, '@@' + name, title,
                permission=permission
                )
        else:
            actions = []

        schema, for_, bases, template, fields = normalize(
            _context, schema, for_, class_, template, 'editwizard.pt', 
            fields=None, omit=None, view=EditWizardView
            )

        self.schema = schema
        self.for_ = for_
        self.bases = bases
        self.template = template
        self.all_fields = fields

        self.panes = []
        self.actions = actions

    def pane(self, _context, fields, label=''):
        fields = [str(f) for f in fields.split(' ')]

        for f in fields:
            if f not in self.all_fields:
                raise ValueError(
                    'Field name is not in schema', 
                    name, self.schema
                    )
        self.panes.append(Pane(fields, label))
        return []

    def __call__(self):
        self.actions.append(
            Action(
                discriminator=(
                    'view', self.for_, self.name, IBrowserPresentation, 
                    self.layer
                    ),
                callable=EditWizardViewFactory,
                args=(
                    self.name, self.schema, self.permission, self.layer, 
                    self.panes, self.all_fields, self.template, 'editwizard.pt',
                    self.bases, self.for_, self.menu, u'', self.use_session
                    )
                )
            )
        return self.actions


def EditWizardViewFactory(name, schema, permission, layer,
                    panes, fields, template, default_template, bases, for_, 
                    menu=u'', usage=u'', use_session=True):
    # XXX What about the __implements__ of the bases?
    class_ = SimpleViewClass(template, used_for=schema, bases=bases)
    class_.schema = schema
    class_.panes = panes
    class_.fieldNames = fields
    class_.use_session = use_session

    class_.generated_form = ViewPageTemplateFile(default_template)

    class_.usage = usage or (
        menu and globalBrowserMenuService.getMenuUsage(menu))

    defineChecker(
        class_,
        NamesChecker(("__call__", "__getitem__", "browserDefault"), permission)
        )

    provideView(for_, name, IBrowserPresentation, class_, layer)


