##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Module containing custom widget definitions.

$Id: widgets.py,v 1.1 2003/06/10 14:40:44 srichter Exp $
"""
import re
from zope.app.form.browser import TextAreaWidget
from book.messageboard.fields import forbidden_regex, allowed_regex

class HTMLSourceWidget(TextAreaWidget):

    def _toFieldValue(self, input):
        input = super(HTMLSourceWidget, self)._toFieldValue(input)

        if self.context.forbidden_tags:
            regex = forbidden_regex %'|'.join(
                self.context.forbidden_tags)
            input = re.sub(regex, '', input)

        if self.context.allowed_tags:
            regex = allowed_regex %'(?: |/)|'.join(
                self.context.allowed_tags)
            input = re.sub(regex, '', input)

        return input

