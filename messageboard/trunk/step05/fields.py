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
"""Module containing custom field definitions.

$Id$
"""
import re

from zope.schema import Text
from zope.schema.interfaces import ValidationError

forbidden_regex = r'</?(?:%s).*?/?>'
allowed_regex = r'</??(?!%s)[a-zA-Z0-9]*? ?(?:[a-z0-9]*?=?".*?")*/??>'

class ForbiddenTags(ValidationError):
    __doc__ = u"""Forbidden HTML Tags used."""


class HTML(Text):
  
    allowed_tags = ()
    forbidden_tags = ()

    def __init__(self, allowed_tags=(), forbidden_tags=(), **kw):
        self.allowed_tags = allowed_tags
        self.forbidden_tags = forbidden_tags
        super(HTML, self).__init__(**kw)

    def _validate(self, value):
        super(HTML, self)._validate(value)

        if self.forbidden_tags:
            regex = forbidden_regex %'|'.join(self.forbidden_tags)
            if re.findall(regex, value):
                raise ForbiddenTags(value, self.forbidden_tags)

        if self.allowed_tags:
            regex = allowed_regex %'|'.join(self.allowed_tags)
            if re.findall(regex, value):
                raise ForbiddenTags(value, self.allowed_tags)


