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
"""
$Id: metadirectives.py,v 1.1 2003/08/03 20:58:38 philikon Exp $
"""

from zope.interface import Interface
from zope.configuration.fields import GlobalObject, Tokens, Path
from zope.schema import TextLine

class IRegisterTranslationsDirective(Interface):

    directory = Path(
        title=u"Directory",
        description=u"Directory containing the translations",
        required=True
        )

class IDefaultLanguagesDirective(Interface):

    languages = Tokens(
        title=u"Languages",
        description=u"Use these as default languages",
        required=True,
        value_type=TextLine()
        )
