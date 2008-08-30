##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Term support for schema.

$Id:$
"""

import zope.interface
import zope.interface.declarations
from zope.schema import interfaces


# ITerm
class SimpleTerm(object):
    """Simple tokenized term implementation."""

    zope.interface.implements(interfaces.ITokenizedTerm)

    _title = None

    def __init__(self, value, token=None, title=None):
        """Create a term for value and token. If token is omitted,
        str(value) is used for the token.  If title is provided, 
        term implements ITitledTokenizedTerm. If we change a title after the
        initiaization we will adjust the ITitledTokenizedTerm support
        """
        self.value = value
        if token is None:
            token = value
        self.token = str(token)
        self.title = title

    @apply
    def title():
        def get(self):
            return self._title
        def set(self, title):
            self._title = title
            if self._title is None:
                if interfaces.ITitledTokenizedTerm.providedBy(self):
                    zope.interface.declarations.noLongerProvides(self,
                        interfaces.ITitledTokenizedTerm)
            else:
                zope.interface.declarations.alsoProvides(self,
                    interfaces.ITitledTokenizedTerm)
        return property(get, set)


class Term(object):
    """Term implementation."""

    zope.interface.implements(interfaces.ITerm)

    def __init__(self, value):
        """Create a term for value.
        """
        self.value = value


class TokenizedTerm(object):
    """Tokenized term implementation."""

    zope.interface.implements(interfaces.ITokenizedTerm)

    def __init__(self, value, token=None):
        """Create a term for value and token. If token is omitted,
        str(value) is used for the token.
        """
        self.value = value
        if token is None:
            token = value
        self.token = str(token)


class TitledTokenizedTerm(object):
    """Title tokenized term implementation."""

    zope.interface.implements(interfaces.ITitledTokenizedTerm)

    def __init__(self, value, token=None, title=None):
        """Create a term for value, token and title. If token is omitted,
        str(value) is used for the token.
        """
        self.value = value
        if token is None:
            token = value
        self.token = str(token)
        self.title = title
