##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""A utility for managing registrations."""

from gocept.registration import registrations

class TestingRegistrations(registrations.Registrations):
    "A registrations object that produces a non-obfuscated hash for testing."

    def __init__(self, context):
        super(TestingRegistrations, self).__init__()

    def _createHash(self, email, data=None):
        return email + '-hash'
