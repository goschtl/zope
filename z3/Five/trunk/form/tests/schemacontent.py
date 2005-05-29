##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Demo schema content

$Id$
"""
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass

from zope.interface import implements, Interface
from zope.schema import TextLine, Text, Object, Int
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget

class IFieldContent(Interface):

    title = TextLine(
        title=u"Title",
        description=u"A short description of the event.",
        default=u"",
        required=True
        )

    description = Text(
        title=u"Description",
        description=u"A long description of the event.",
        default=u"",
        required=False
        )

    somenumber = Int(
        title=u"Some number",
        default=0,
        required=False
        )

class FieldContent(SimpleItem):
    """A Viewable piece of content with fields"""
    implements(IFieldContent)
    meta_type = 'Five FieldContent'

    def __init__(self, id, title):
        self.id = id
        self.title = title

InitializeClass(FieldContent)

def manage_addFieldContent(self, id, title, REQUEST=None):
    """Add the field content"""
    id = self._setObject(id, FieldContent(id, title))
    return ''

class IComplexSchemaContent(Interface):
    
    fishtype = TextLine(
        title=u"Fish type",
        description=u"The type of fish",
        default=u"It was a lovely little fish. And it went wherever I did go.",
        required=False)

    fish = Object(
        title=u"Fish",
        schema=IFieldContent,
        description=u"The fishy object",
        required=True)

class ComplexSchemaContent(SimpleItem):
     implements(IComplexSchemaContent)
     meta_type ="Five ComplexSchemaContent"

     def __init__(self, id):
         self.id = id
         self.fish = FieldContent('fish', 'title')
         self.fish.description = ""
         self.fishtype = 'Lost fishy'

class ComplexSchemaView:
    """Needs a docstring"""
    
    fish_widget = CustomWidgetFactory(ObjectWidget, FieldContent)

InitializeClass(ComplexSchemaContent)

def manage_addComplexSchemaContent(self, id, REQUEST=None):
    """Add the complex schema content"""
    id = self._setObject(id, ComplexSchemaContent(id))
    return ''
