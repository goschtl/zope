##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Password managers

$Id$
"""
__docformat__ = 'restructuredtext'

# BBB: the password managers were moved into zope.password package.
from zope.password.password import (
    PlainTextPasswordManager,
    MD5PasswordManager,
    SHA1PasswordManager,
    SSHAPasswordManager
    )
from zope.password.interfaces import IPasswordManager
from zope.password.vocabulary import PasswordManagerNamesVocabulary

# Simple registry used by mkzopeinstance script
managers = [
    ("Plain Text", PlainTextPasswordManager()), # default
    ("MD5", MD5PasswordManager()),
    ("SHA1", SHA1PasswordManager()),
    ("SSHA", SSHAPasswordManager()),
]
