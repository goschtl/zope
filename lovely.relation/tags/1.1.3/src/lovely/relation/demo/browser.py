##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

from zope.app.form.browser.textwidgets import TextWidget

class NamesWidget(TextWidget):

    def __init__(self, list, choice, request):
        super(NamesWidget, self).__init__(list, request)
        self.vocabulary = choice.vocabulary

    def _toFieldValue(self, input):
        value = super(NamesWidget, self)._toFieldValue(input)
        if not value:
            return u''
        value = value.split(u',')
        return [self.vocabulary.getTermByToken(t.strip()).value \
                for t in value]

    def _toFormValue(self, value):
        return u', '.join([self.vocabulary.getTerm(v).token for v in value])

