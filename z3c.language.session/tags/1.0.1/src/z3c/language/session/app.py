##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
__docformat__ = 'restructuredtext'

import zope.interface

from zope.session.session import Session

from z3c.language.session import ILanguageSession
from z3c.language.session import IGetLanguage
from z3c.language.session import ISetLanguage
from z3c.language.session import sessionPkgDataId


class LanguageSession(Session):
    """Can get and set a language in session."""

    zope.interface.implements(ILanguageSession, IGetLanguage, ISetLanguage)

    def __init__(self, request):
        super(LanguageSession, self).__init__(request)

    def getLanguage(self):
        """Returns the language form the session."""
        spd = self.get(sessionPkgDataId, {})
        return spd.get('language', None)

    def setLanguage(self, language):
        """Set the language to the session."""
        spd = self.__getitem__(sessionPkgDataId)
        spd['language'] = language
