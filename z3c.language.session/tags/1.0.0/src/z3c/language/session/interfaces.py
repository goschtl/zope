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
from zope.schema.interfaces import IVocabularyTokenized
from zope.session.interfaces import ISession

from z3c.i18n import MessageFactory as _

sessionPkgDataId = 'z3c.language.session.SessionDataContainer'



class ILanguageSession(ISession):
    """Session containing the language for a session."""



class IHasLanguage(zope.interface.Interface):
    """Has language API"""

    def hasLanguage():
        """View for to check if a session has a i18n language value."""



class IGetLanguage(zope.interface.Interface):
    """Get language API"""

    def getLanguage():
        """View for to check if a session has a i18n language value."""



class ISetLanguage(zope.interface.Interface):
    """Set language API"""

    def setLanguage():
        """Set the given language in the request to the session.
        
        You can do it via the javascript sessionlanguage.js with the
        javascript method setLanguage:
        
        javascript:setLanguage('@@setLanguage','de')
        
        Or send the request to the view '@@setLanguage'. There has to be a 
        variable 'language' and 'nextURL' in the request like
        """

