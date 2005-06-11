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
"""Test helpers

$Id$
"""
import urllib

from OFS.Folder import Folder
from OFS.interfaces import IFolder
from AccessControl import Unauthorized
from Testing.ZopeTestCase import ZopeTestCase

from zope.interface import implements
from Products.Five.traversable import Traversable

def add_and_edit(self, id, REQUEST):
    """Helper function to point to the object's management screen if
    'Add and Edit' button is pressed.
    id -- id of the object we just added
    """
    if REQUEST is None:
        return
    try:
        u = self.DestinationURL()
    except:
        u = REQUEST['URL1']
    if REQUEST.has_key('submit_edit'):
        u = "%s/%s" % (u, urllib.quote(id))
    REQUEST.RESPONSE.redirect(u+'/manage_main')

class NoVerifyPasteFolder(Folder):
    """Folder that does not perform paste verification.
    Used by test_events
    """
    def _verifyObjectPaste(self, object, validate_src=1):
        pass

def manage_addNoVerifyPasteFolder(container, id, title=''):
    container._setObject(id, NoVerifyPasteFolder())
    folder = container[id]
    folder.id = id
    folder.title = title

class FiveTraversableFolder(Traversable, Folder):
    """Folder that is five-traversable
    """
    implements(IFolder)

def manage_addFiveTraversableFolder(container, id, title=''):
    container._setObject(id, FiveTraversableFolder())
    folder = container[id]
    folder.id = id
    folder.title = title

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
