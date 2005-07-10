##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Restricted python test helpers

$Id$
"""
from AccessControl import Unauthorized
from Testing.ZopeTestCase import ZopeTestCase

class RestrictedPythonTestCase(ZopeTestCase):
    """Test whether code is really restricted.

    Kind permission from Plone to use this."""

    def addPS(self, id, params='', body=''):
        # clean up any 'ps' that's already here..
        try:
            self.folder._getOb(id)
            self.folder.manage_delObjects([id])
        except AttributeError:
            pass # it's okay, no 'ps' exists yet
        factory = self.folder.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript(id)
        self.folder[id].ZPythonScript_edit(params, body)

    def check(self, psbody):
        self.addPS('ps', body=psbody)
        try:
            self.folder.ps()
        except (ImportError, Unauthorized), e:
            self.fail(e)

    def checkUnauthorized(self, psbody):
        self.addPS('ps', body=psbody)
        try:
            self.folder.ps()
        except (AttributeError, Unauthorized):
            pass
        else:
            self.fail("Authorized but shouldn't be")
