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
"""Edit Wizard View Classes

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security.checker import defineChecker, NamesChecker

from zope.app import zapi
from zope.event import notify
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.location.interfaces import ILocation
from zope.app.location import LocationProxy


from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser.globalbrowsermenuservice import \
     globalBrowserMenuService

from editview import EditView
from submit import Next, Previous, Update
from zope.app.form.interfaces import WidgetInputError, WidgetsError
from zope.app.form.utility \
        import setUpEditWidgets, getWidgetsData, applyWidgetsChanges


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
        adapted = self.schema(self.context)
        if adapted is not self.context:
            if not ILocation.providedBy(adapted):
                adapted = LocationProxy(adapted)
            adapted.__parent__ = self.context
        self.adapted = adapted

        if self.use_session:
            # Need session for File upload fields
            raise NotImplementedError, \
                'Cannot be implemented until we have an ISessionDataManager'
        else:
            self.storage = WizardStorage(self.fieldNames, adapted)

        # Add all our widgets as attributes on this view
        setUpEditWidgets(self, self.schema, source=self.storage,
                         names=self.fieldNames)

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
        '''Called before rendering each pane. It is responsible
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
            names = self.currentPane().names
            data = getWidgetsData(self, self.schema, names=names)
            self.errors = {}
        except WidgetsError, errors:
            x = {}
            for k, label, msg in errors:
                x[k] = msg
            self.errors = x
        else:

            self.storage.update(data)

            if Next in self.request:
                self._current_pane_idx += 1
                assert self._current_pane_idx < len(self.panes)
            elif Previous in self.request:
                self._current_pane_idx -= 1
                assert self._current_pane_idx >= 0
            elif Update in self.request:
                if not self.use_session:
                    # Data from panes other than the current one is still
                    # stuck in request
                    self.storage.update(getWidgetsData(
                        self, self.schema, names=self.fieldNames))
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
                    getattr(self, k+'_widget').getInputValue()
            self.show_submit = 1
        except WidgetInputError:
            self.show_submit = 0

        self.show_next = (self._current_pane_idx < len(self.panes) - 1)

        self.show_previous = self._current_pane_idx > 0

    def apply_update(self, storage):
        ''' Save changes to our content object '''
        for k,v in storage.items():
            getattr(self,k+'_widget').setRenderedValue(v)
        content = self.adapted
        changed = applyWidgetsChanges(self, self.schema, target=content,
                names=self.fieldNames)
        # We should not generate events when an adapter is used.
        # That's the adapter's job
        if changed and self.context is self.adapted:
            notify(ObjectModifiedEvent(content))
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
                    widget = getattr(self, k+'_widget')
                    out(widget.hidden())
            return ''.join(olist)


def EditWizardViewFactory(name, schema, permission, layer,
                    panes, fields, template, default_template, bases, for_,
                    menu=u'', use_session=False):
    # XXX What about the __implements__ of the bases?
    class_ = SimpleViewClass(template, used_for=schema, bases=bases)
    class_.schema = schema
    class_.panes = panes
    class_.fieldNames = fields
    class_.use_session = use_session

    class_.generated_form = ViewPageTemplateFile(default_template)

    defineChecker(
        class_,
        NamesChecker(("__call__", "__getitem__", "browserDefault"), permission)
        )

    s = zapi.getGlobalService(zapi.servicenames.Presentation)
    s.provideView(for_, name, IBrowserRequest, class_, layer)


