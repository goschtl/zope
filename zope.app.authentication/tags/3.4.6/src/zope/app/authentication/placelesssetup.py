##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Pluggable Authentication Service Placeless Setup

$Id$
"""
__docformat__ = "reStructuredText"

from zope.app.testing import ztapi
from zope.app.authentication.interfaces import IPasswordManager
from zope.app.authentication.password import PlainTextPasswordManager
from zope.app.authentication.password import MD5PasswordManager
from zope.app.authentication.password import SHA1PasswordManager
from zope.app.authentication.password import SSHAPasswordManager

class PlacelessSetup(object):

    def setUp(self):
        ztapi.provideUtility(IPasswordManager, PlainTextPasswordManager(),
            "Plain Text")
        ztapi.provideUtility(IPasswordManager, MD5PasswordManager(), "MD5")
        ztapi.provideUtility(IPasswordManager, SHA1PasswordManager(), "SHA1")
        ztapi.provideUtility(IPasswordManager, SHA1PasswordManager(), "SSHA")