##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH and Contributors.
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

import transaction
import z3c.zalchemy
from zope.app.testing import setup
from z3c.zalchemy.datamanager import AlchemyEngineUtility
from zope import component
import os, tempfile, shutil


def setUp(test):
    pass

def tearDown(test):
    if z3c.zalchemy.inSession():
        transaction.get().commit()

def placefulSetUp(test):
    setup.placefulSetUp()
    test.tmpDir = tempfile.mkdtemp()
    dbFile = os.path.join(test.tmpDir,'z3c.zalchemy.testing.placefull.db')
    engineUtil = AlchemyEngineUtility(
        'database','sqlite:///%s' % dbFile)
    component.provideUtility(engineUtil)
    test.globs['engineUtil'] = engineUtil

def placefulTearDown(test):
    setup.placefulTearDown()
    tearDown(test)
    shutil.rmtree(test.tmpDir)
    
