##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Browser widgets for bug tracker

$Id: textwidgets.py 25318 2004-06-09 21:00:59Z garrett $
"""
from zope.proxy import removeAllProxies
from zope.schema import Choice

from zope.app.form.browser import TextAreaWidget
from zope.app.form.browser.itemswidgets import ChoiceInputWidget

from bugtracker.renderable import RenderableText

choice = Choice(
    title=u'Type',
    description=u'Type of the text above',
    default='zope.source.rest',
    required=True,
    vocabulary='SourceTypes')


class RenderableTextAreaWidget(TextAreaWidget):

    def _getTypeWidget(self):
        bound_choice = choice.bind(self.context.context)
        bound_choice.__name__ = self.context.__name__ + '_ttype'
        widget = ChoiceInputWidget(bound_choice, self.request)
        attr = getattr(self.context.context, self.context.__name__, None)
        widget.setRenderedValue(getattr(attr, 'ttype', choice.default))
        return widget

    def __call__(self):
        html = super(RenderableTextAreaWidget, self).__call__()
        html += '\n<br />\n'
        html += self._getTypeWidget()()
        return html

    def _toFieldValue(self, value):
        value = super(RenderableTextAreaWidget, self)._toFieldValue(value)
        ttype = self._getTypeWidget().getInputValue()
        return RenderableText(value, ttype)
        
    def applyChanges(self, content):
        field = self.context
        value = self.getInputValue()
        current = field.query(content, self)

        if unicode(value) == unicode(current) and \
           value.ttype == getattr(current, 'ttype', object()):
            return False
        else:
            field.set(content, value)
            return True
