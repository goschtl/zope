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
$Id: EditView.py,v 1.4 2002/12/11 13:55:59 jim Exp $
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

    # Fall-back field names computes from schema
    fieldNames = property(lambda self: fieldNames(self.schema))
        
    def __init__(self, context, request):
        super(EditView, self).__init__(context, request)
        setUpEditWidgets(self, self.schema, names=self.fieldNames)

    def setPrefix(self, prefix):
        for widget in self.widgets():
            widget.setPrefix(prefix)

    def widgets(self):
        return [getattr(self, name)
                for name in self.fieldNames
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
                data = getWidgetsData(self, self.schema,
                                      required=0, names=self.fieldNames)
                unchanged = self.apply_update(data)
            except WidgetsError, errors:
                self.errors = errors
                return u"An error occured."
            except Exception, v:
                self.errors = (v, )
                return u"An error occured."
            else:
                setUpEditWidgets(self, self.schema, force=1,
                                 names=self.fieldNames)
                if not unchanged:
                    return "Updated %s" % datetime.utcnow()

        return ''


def EditViewFactory(name, schema, label, permission, layer,
                    template, default_template, bases, for_, fields):

    class_  = SimpleViewClass(
        template,
        used_for = schema, bases = bases
        )

    class_.schema = schema
    class_.label = label
    class_.fieldNames = fields

    class_.generated_form = ViewPageTemplateFile(default_template)

    defineChecker(class_,
                  NamesChecker(
                    ("__call__", "__getitem__", "browserDefault"),
                    permission,
                    )
                  )

    provideView(for_, name, IBrowserPresentation, class_, layer)
                  

def _normalize(_context, schema_, for_, class_, template, default_template,
               fields, omit):
    schema = _context.resolve(schema_)

    if for_ is None:
        for_ = schema
    else:
        for_ = _context.resolve(for_)

    if class_ is None:
        bases = (EditView, )
    else:
        bases = (_context.resolve(class_), EditView)
        

    if template is not None:
        template = _context.path(template)
    else:
        template = default_template

    template = str(template)

    names = fieldNames(schema)
    
    if fields:
        fields = fields.split()
        for name in fields:
            if name not in names:
                raise ValueError("Field name %s is not in schema %s",
                                 name, schema_)
    else:
        fields = names

    if omit:
        omit = omit.split()
        for name in omit:
            if name not in names:
                raise ValueError("Field name %s is not in schema %s",
                                 name, schema_)
        fields = [name for name in fields if name not in omit]

    return schema, for_, bases, template, fields

def edit(_context, name, schema, label,
              permission = 'Zope.Public', layer = "default",
              class_ = None, for_ = None,
              template = None, omit=None, fields=None):

    (schema, for_, bases, template, fields,
     ) = _normalize(
        _context, schema, for_, class_, template, 'edit.pt', fields, omit)

    return [
        Action(
        discriminator = ('http://namespaces.zope.org/form/edit',
                         name, for_, layer),
        callable = EditViewFactory,
        args = (name, schema, label, permission, layer, template, 'edit.pt',
                bases,
                for_, fields),
        )
        ]

def subedit(_context, name, schema, label,
              permission = 'Zope.Public', layer = "default",
              class_ = None, for_ = None,
              template = None, omit=None, fields=None):

    (schema, for_, bases, template, fields,
     ) = _normalize(
        _context, schema, for_, class_, template, 'subedit.pt', fields, omit)

    return [
        Action(
        discriminator = ('http://namespaces.zope.org/form/subedit',
                         name, for_, layer),
        callable = EditViewFactory,
        args = (name, schema, label, permission, layer, template, 'subedit.pt',
                bases,
                for_, fields),
        )
        ]


