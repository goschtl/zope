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
"""Support for display-only pages based on schema.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app import zapi

from zope.schema import getFieldNamesInOrder

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.location.interfaces import ILocation
from zope.app.location import LocationProxy
from zope.app.publisher.browser import BrowserView
from zope.security.checker import defineChecker, NamesChecker

from zope.app.form.utility import setUpDisplayWidgets
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass

class DisplayView(BrowserView):
    """Simple display-view base class.

    Subclasses should provide a `schema` attribute defining the schema
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
        adapted = self.schema(self.context)
        if adapted is not self.context:
            if not ILocation.providedBy(adapted):
                adapted = LocationProxy(adapted)
            adapted.__parent__ = self.context
        self.adapted = adapted
        setUpDisplayWidgets(self, self.schema, source=adapted,
                            names=self.fieldNames)

    def setPrefix(self, prefix):
        for widget in self.widgets():
            widget.setPrefix(prefix)

    def widgets(self):
        return [getattr(self, name+'_widget')
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
    s = zapi.getGlobalService(zapi.servicenames.Presentation)
    s.provideView(for_, name, IBrowserRequest, class_, layer)
