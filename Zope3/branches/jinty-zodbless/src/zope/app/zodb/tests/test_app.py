##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
import doctest

import transaction
from ZODB.DB import DB
from ZODB.DemoStorage import DemoStorage
from zope.app.folder import rootFolder
from zope.publisher.base import TestPublication
from zope.publisher.browser import TestRequest
from zope.app.applicationcontrol.applicationcontrol \
     import applicationController, applicationControllerRoot

from zope.app.zodb import ROOT_NAME
from zope.app.zodb.app import ZODBApplicationFactory

def setUp(test):
    transaction.begin()

    storage = DemoStorage('test_storage')
    db = DB(storage)

    connection = db.open()
    root = connection.root()
    app = rootFolder()
    root[ROOT_NAME] = app
    transaction.commit()

    connection.close()

    test.globs['app'] = app
    test.globs['resource_factory'] = ZODBApplicationFactory(db)

def createRequest(path, publication, **kw):
    request = TestRequest(PATH_INFO=path, **kw)
    request.setPublication(publication)
    return request

def testGetApplication():
    """
    Make sure that if we call the resource_factory, we get the application
    object:

        >>> r = createRequest('/foo', TestPublication(None))
        >>> app is resource_factory(r)
        True
    """

def testTraverseNameApplicationControl():
    # XXX - applicationControllerRoot traversal should not be tested here.
    #r = self._createRequest('/++etc++process', TestPublication(None))
    #ac = pub.traverseName(r,
    #                      applicationControllerRoot,
    #                      '++etc++process')
    #self.assertEqual(ac, applicationController)
    """
    Make sure that if we traverse to /++etc++process, we get the application controller root.

        >>> r = createRequest('/++etc++process', TestPublication(None))
        >>> acr = resource_factory(r)
        >>> acr is applicationControllerRoot
        True
    """

def test_suite():
    return doctest.DocTestSuite(setUp=setUp)
