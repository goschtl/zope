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
"""Code Interpreter Service Directives

$Id: metadirectives.py,v 1.2 2003/08/21 14:19:24 srichter Exp $
"""
from zope.interface import Interface
from zope.configuration.fields import GlobalObject
from zope.schema import TextLine

class IRegisterInterpreterDirective(Interface):

    type = TextLine(
        title=u"Type",
        description=u"Type/name of the language in content type format.",
        required=True)

    component = GlobalObject(
        title=u"Interpreter Component",
        description=u"Path to the interpreter instance.",
        required=True)

