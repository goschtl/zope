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
$Id: EditView.py,v 1.3 2002/12/01 10:22:33 jim Exp $
"""

from datetime import datetime
from Zope.Event import publish
from Zope.Event.ObjectEvent import ObjectModifiedEvent
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.Forms.Views.Browser import Widget
from Zope.App.Forms.Exceptions import WidgetsError
from Zope.App.Forms.Utility import setUpEditWidgets, getWidgetsData
from Zope.App.Forms.Utility import haveWidgetsData, fieldNames
from Zope.Configuration.Action import Action
from Zope.App.PageTemplate.ViewPageTemplateFile import ViewPageTemplateFile
from Zope.Security.Checker import defineChecker, NamesChecker
from Zope.ComponentArchitecture.GlobalViewService import provideView
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.App.PageTemplate.SimpleViewClass import SimpleViewClass
from Zope.App.Forms.Browser.StandardSubmit import Update


class EditView(BrowserView):
    """Simple edit-view base class

    Subclasses should provide a schema attribute defining the schema
    to be edited.
    """

    errors = ()
    label = ''

    generated_form = index = ViewPageTemplateFile('edit.pt')

    def __init__(self, context, request):
        super(EditView, self).__init__(context, request)
        setUpEditWidgets(self, self.schema)

    def setPrefix(self, prefix):
        for widget in self.widgets():
            widget.setPrefix(prefix)

    def __call__(self, *args, **kw):
        return self.index(*args, **kw)

    def widgets(self):
        return [getattr(self, name)
                for name in fieldNames(self.schema)
                ]

    def apply_update(self, data):
        """Apply data updates

        Return true if data were unchanged and false otherwise.
        This sounds backwards, but it allows lazy implementations to
        avoid tracking changes.
        """
            
        content = self.context

        errors = []
        unchanged = True

        for name in data:
            # OK, we really got a field
            try:
                newvalue = data[name]

                # We want to see if the data changes. Unfortunately,
                # we don't know enough to know that we won't get some
                # strange error, so we'll carefully ignore errors and
                # assume we should update the data if we can't be sure
                # it's the same.

                change = True
                try:
                    # Use self as a marker
                    change = getattr(content, name, self) != newvalue
                except:
                    pass

                if change:
                    setattr(content, name, data[name])
                    unchanged = False

            except Exception, v:
                errors.append(v)

        if errors:
            raise WidgetsError(*errors)

        if not unchanged:
            publish(content, ObjectModifiedEvent(content))

        return unchanged

    def update(self):
        if Update in self.request:
            unchanged = True
            try:
                data = getWidgetsData(self, self.schema, required=0)
                unchanged = self.apply_update(data)
            except WidgetsError, errors:
                self.errors = errors
                return u"An error occured."
            except Exception, v:
                self.errors = (v, )
                return u"An error occured."
            else:
                setUpEditWidgets(self, self.schema, force=1)
                if not unchanged:
                    return "Updated %s" % datetime.utcnow()

        return ''

    

def EditViewFactory(name, schema, label, permission, layer,
                    template, class_, for_):

    if class_ is None:
        bases = EditView,
    else:
        bases = class_, EditView
    
    class_  = SimpleViewClass(
        template,
        used_for = schema, bases = bases
        )

    class_.schema = schema
    class_.label = label

    defineChecker(class_,
                  NamesChecker(
                    ("__call__", "__getitem__", "browserDefault"),
                    permission,
                    )
                  )

    provideView(for_, name, IBrowserPresentation, class_, layer)
                  
        

def directive(_context, name, schema, label,
              permission = 'Zope.Public', layer = "default",
              class_ = None, for_ = None,
              template = None):

    schema = _context.resolve(schema)
    if for_ is None:
        for_ = schema
    else:
        for_ = _context.resolve(for_)
    if class_ is not None:
        class_ = _context.resolve(class_)
    if template is not None:
        template = _context.path(template)
    else:
        template = 'edit.pt'

    template = str(template)

    return [
        Action(
        discriminator = ('http://namespaces.zope.org/form/edit',
                         name, for_, layer),
        callable = EditViewFactory,
        args = (name, schema, label, permission, layer, template, class_,
                for_),
        )
        ]


