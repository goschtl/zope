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

$Id: BrowserWidget.py,v 1.2 2002/06/10 23:27:49 jim Exp $
"""

from IBrowserWidget import IBrowserWidget
from Zope.App.Formulator.Widget import Widget
from Zope.App.Formulator.IPropertyFieldAdapter import IPropertyFieldAdapter
from Zope.ComponentArchitecture import getAdapter


class BrowserWidget(Widget):
    """A field widget that knows how to display itself as HTML.
    """

    __implements__ = IBrowserWidget

    propertyNames = Widget.propertyNames + \
                    ['tag', 'type', 'cssClass', 'hidden', 'extra']
    
    tag = 'input'
    type = 'text'
    cssClass = ''
    hidden = 0
    extra = ''

    def getValueFromRequest(self, REQUEST):
        """ """
        return REQUEST.get('field_'+self.context.id, None)


    def _getValueToInsert(self, REQUEST):
        """ """
        field = self.context
        if REQUEST and (('field_'+field.id) in REQUEST):
            return REQUEST['field_'+field.id]
        else:
            return getAdapter(field, IPropertyFieldAdapter).\
                   getPropertyInContext()
            

    def render(self, REQUEST=None):
        """Renders this widget as HTML using property values in field.
        """
        return renderElement(self.getValue('tag'),
                             type = self.getValue('type'),
                             name = self.context.id,
                             value = self._getValueToInsert(REQUEST),
                             cssClass = self.getValue('cssClass'),
                             extra = self.getValue('extra'))

        
    def render_hidden(self, REQUEST=None):
        """Renders this widget as a hidden field.
        """
        return renderElement(self.getValue('tag'),
                             type = 'hidden',
                             name = self.context.id,
                             value = self._getValueToInsert(REQUEST),
                             cssClass = self.getValue('cssClass'),
                             extra = self.getValue('extra'))



def renderTag(tag, **kw):
    """Render the tag. Well, not all of it, as we may want to / it.
    """
    attr_list = []

    kw['name'] = 'field_' + kw['name']

    # special case handling for css_class
    if 'cssClass' in kw:
        if kw['cssClass'] != "":
            attr_list.append('class="%s"' % kw['cssClass'])
        del kw['cssClass']

    # special case handling for extra 'raw' code
    if 'extra' in kw:
        extra = kw['extra'] # could be empty string but we don't care
        del kw['extra']
    else:
        extra = ""

    # handle other attributes
    for key, value in kw.items():
        if value == None:
            value = key
        attr_list.append('%s="%s"' % (key, str(value)))
            
    attr_str = " ".join(attr_list)
    return "<%s %s %s" % (tag, attr_str, extra)


def renderElement(tag, **kw):
    if 'contents' in kw:
        contents = kw['contents']
        del kw['contents']
        return "%s>%s</%s>" % (apply(renderTag, (tag,), kw), contents, tag)
    else:
        return apply(renderTag, (tag,), kw) + " />"
    






