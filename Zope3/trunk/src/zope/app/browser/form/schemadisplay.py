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
"""\
Support for display-only pages based on schema.

$Id: schemadisplay.py,v 1.2 2003/04/30 23:37:51 faassen Exp $
"""

from zope.schema import getFieldNamesInOrder

from zope.configuration.action import Action
from zope.proxy.context import ContextWrapper
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.publisher.browser import BrowserView
from zope.security.checker import defineChecker, NamesChecker
from zope.component.view import provideView
from zope.component import getAdapter

from zope.app.form.utility import setUpDisplayWidgets
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass

from zope.app.publisher.browser.globalbrowsermenuservice \
     import menuItemDirective, globalBrowserMenuService

# XXX perhaps a little too intimate?
from zope.app.browser.form.editview import normalize


class DisplayView(BrowserView):
    """Simple display-view base class.

    Subclasses should provide a schema attribute defining the schema
    to be displayed.
    """

    errors = ()
    update_status = ''
    label = ''

    # Fall-back field names computes from schema
    fieldNames = property(lambda self: getFieldNamesInOrder(self.schema))

    def __init__(self, context, request):
        super(DisplayView, self).__init__(context, request)
        self._setUpWidgets()

    def _setUpWidgets(self):
        adapted = getAdapter(self.context, self.schema)
        if adapted is not self.context:
            adapted = ContextWrapper(adapted, self.context, name='(adapted)')
        self.adapted = adapted
        setUpDisplayWidgets(self, self.schema, names=self.fieldNames,
                            content=adapted)

    def setPrefix(self, prefix):
        for widget in self.widgets():
            widget.setPrefix(prefix)

    def widgets(self):
        return [getattr(self, name)
                for name in self.fieldNames]


def DisplayViewFactory(name, schema, label, permission, layer,
                       template, default_template, bases, for_, fields,
                       fulledit_path=None, fulledit_label=None, menu=u'',
                       usage=u''):
    # XXX What about the __implements__ of the bases?
    class_ = SimpleViewClass(template, used_for=schema, bases=bases)
    class_.schema = schema
    class_.label = label
    class_.fieldNames = fields
    class_.fulledit_path = fulledit_path
    if fulledit_path and (fulledit_label is None):
        fulledit_label = "Full display"
    class_.fulledit_label = fulledit_label
    class_.generated_form = ViewPageTemplateFile(default_template)
    class_.usage = usage or (
        menu and globalBrowserMenuService.getMenuUsage(menu)
        )
    defineChecker(class_,
                  NamesChecker(("__call__", "__getitem__", "browserDefault"),
                               permission))
    provideView(for_, name, IBrowserPresentation, class_, layer)


def display(_context, name, schema, permission, label='',
            layer="default",
            class_=None, for_=None,
            template=None, omit=None, fields=None,
            menu=None, title='Display', usage=u''):
    actions = []
    if menu:
        actions = menuItemDirective(
            _context, menu, for_ or schema, '@@' + name, title,
            permission=permission)

    schema, for_, bases, template, fields = normalize(
        _context, schema, for_, class_, template, 'display.pt', fields, omit,
        DisplayView)

    actions.append(Action(
        discriminator=('view', for_, name, IBrowserPresentation, layer),
        callable=DisplayViewFactory,
        args=(name, schema, label, permission, layer, template, 'display.pt',
              bases, for_, fields, menu, usage)))
    return actions
