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
from zope import interface

SESSIONKEY = 'z3ext.statusmessage'


class StatusMessageError(Exception):
    """ general message service error """


class IMessage(interface.Interface):
    """ message """

    message = interface.Attribute('Message text')


class IMessageFactory(interface.Interface):
    """ message factory """

    def __call__(message):
        """ create IMessage with message """


class IInformationMessage(IMessage):
    """ information message """


class IWarningMessage(IMessage):
    """ wranning message """


class IErrorMessage(IMessage):
    """ error message """


class IStatusMessage(interface.Interface):
    """ message service """

    def add(text, type='info'):
        """ add message text as message to service """

    def addMessage(message):
        """ add IMessage object to service """

    def list():
        """ list all messages """

    def clear():
        """ return all messages and clear service """

    def hasMessages():
        """ check is service has messages """


class IMessageView(interface.Interface):
    """ message view interface """
