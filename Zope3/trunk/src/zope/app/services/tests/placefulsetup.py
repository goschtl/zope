##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

Revision information:
$Id: placefulsetup.py,v 1.23 2003/06/03 21:43:00 jim Exp $
"""

from zope.app import zapi
from zope.app.tests import setup
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.services.servicenames import HubIds
from zope.app.content.folder import RootFolder
from zope.app.context import ContextWrapper

class Place(object):

    def __init__(self, path):
        self.path = path

    def __get__(self, inst, cls=None):
        if inst is None:
            return self

        try: root = inst.rootFolder
        except AttributeError:
            root = inst.rootFolder = setup.buildSampleFolderTree()

        root = ContextWrapper(root, None)
        return zapi.traverse(root, self.path)

class PlacefulSetup(PlacelessSetup):

    # Places :)
    rootFolder  = Place('')
    
    folder1     = Place('folder1')
    folder1_1   = Place('folder1/folder1_1')
    folder1_1_1 = Place('folder1/folder1_1/folder1_1_1')
    folder1_1_2 = Place('folder1/folder1_2/folder1_1_2')
    folder1_2   = Place('folder1/folder1_2')
    folder1_2_1 = Place('folder1/folder1_2/folder1_2_1')

    folder2     = Place('folder2')
    folder2_1   = Place('folder2/folder2_1')
    folder2_1_1 = Place('folder2/folder2_1/folder2_1_1')
    

    def setUp(self, folders=False, site=False):
        setup.placefullSetUp()
        if folders or site:
            return self.buildFolders(site)

    def tearDown(self):
        setup.placefullTearDown()
        # clean up folders and placeful service managers and services too?

    def buildFolders(self, site=False):
        self.rootFolder = setup.buildSampleFolderTree()
        if site:
            return self.makeSite()

    def makeSite(self, path='/'):
        folder = zapi.traverse(self.rootFolder, path)
        return setup.createServiceManager(folder)
        
    def createRootFolder(self):
        self.rootFolder 
        self.rootFolder = RootFolder()

    # The following is a hook that some base classes might want to override.
    def getObjectHub(self):
        from zope.app.services.hub import ObjectHub
        return ObjectHub()

    def createStandardServices(self):
        '''Create a bunch of standard placeful services'''

        setup.createStandardServices(self.rootFolder,
                                     hubids=self.getObjectHub())
    
