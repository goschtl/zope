##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
import cgi
import interfaces
from zope import interface


class Message(object):
    interface.classProvides(interfaces.IMessageFactory)

    def __init__(self, message):
        self.message = message


class InformationMessage(Message):
    interface.implements(interfaces.IInformationMessage)


class WarningMessage(Message):
    interface.implements(interfaces.IWarningMessage)


class ErrorMessage(Message):
    interface.implements(interfaces.IErrorMessage)

    def __init__(self, e):
        if isinstance(e, Exception):
            self.message = '%s: %s'%(e.__class__.__name__, cgi.escape(str(e), True))
        else:
            self.message = e
