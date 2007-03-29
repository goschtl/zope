###############################################################################
#
# Copyright 2006 by refline (Schweiz) AG, CH-5630 Muri
#
###############################################################################
"""Special Fields

$Id$
"""
__docformat__ = "reStructuredText"

import re
import zope.interface
import zope.schema
from z3c.schema.regex import interfaces

class Regex(zope.schema.ASCIILine):
    """Regex schema field.

    Must be a compilable regular expression
    """

    zope.interface.implements(interfaces.IRegex)

    def _validate(self, value):
        super(Regex, self)._validate(value)
        try:
            re.compile(value)
        except re.error, e:
            raise interfaces.InvalidRegex, '%r, %s' % (value, e)

    def fromUnicode(self, value):
        v = str(value.strip())
        self.validate(v)
        return v
