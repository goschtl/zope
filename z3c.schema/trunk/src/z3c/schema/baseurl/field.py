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

from z3c.schema.baseurl import interfaces


isValidBaseURL = re.compile(
    r"[a-zA-z0-9+.-]+:"   # scheme
    r"\S*$"               # non space (should be pickier)
    ).match


class BaseURL(zope.schema.URI):
    """Base URL field.
    
    Such a base url must end with a ``/``. This makes it simpler for
    append a view name.
    """

    zope.interface.implements(interfaces.IBaseURL)

    def _validate(self, value):
        if isValidBaseURL(value) and value.endswith('/') and \
            not value.endswith(':/'):
            return

        raise interfaces.InvalidBaseURL, value

    def fromUnicode(self, value):
        v = str(value.strip())
        self.validate(v)
        return v
