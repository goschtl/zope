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
"""Undo Tests

$Id: test_undo.py,v 1.1 2004/03/01 14:16:56 philikon Exp $
"""
from datetime import datetime
from unittest import TestCase, main, makeSuite

from zope.interface import implements
from zope.publisher.browser import TestRequest

from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.undo.interfaces import IUndoManager
from zope.app.undo.browser import UndoView

class TestIUndoManager:
    implements(IUndoManager)

    def __init__(self):
        dict1 = {'id': '1', 'user_name': 'monkey', 'description': 'thing1',
 'time': 'today', 'datetime': datetime(2001, 01, 01, 12, 00, 00)}
        dict2 = {'id': '2', 'user_name': 'monkey', 'description': 'thing2',
 'time': 'today', 'datetime': datetime(2001, 01, 01, 12, 00, 00)}
        dict3 = {'id': '3', 'user_name': 'bonobo', 'description': 'thing3',
 'time': 'today', 'datetime': datetime(2001, 01, 01, 12, 00, 00)}
        dict4 = {'id': '4', 'user_name': 'monkey', 'description': 'thing4',
 'time': 'today', 'datetime': datetime(2001, 01, 01, 12, 00, 00)}
        dict5 = {'id': '5', 'user_name': 'bonobo', 'description': 'thing5',
 'time': 'today', 'datetime': datetime(2001, 01, 01, 12, 00, 00)}

        self.dummy_db = [dict1, dict2, dict3, dict4, dict5]

    def getUndoInfo(self, first=0, last=-20, user_name=None):
        return self.dummy_db

    def undoTransaction(self, id_list):
        # just remove an element for now
        temp_dict = {}
        for db_record in self.dummy_db:
            if db_record['id'] not in id_list:
                temp_dict[db_record['id']] =  db_record

        self.dummy_db = []
        for key in temp_dict.keys():
            self.dummy_db.append(temp_dict[key])


class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        from zope.component import getService
        getService(None,'Utilities').provideUtility(IUndoManager,
              TestIUndoManager())

    def testGetUndoInfo(self):
        view = UndoView()
        view.context = None
        view.request = TestRequest()
        self.checkResult(view.getUndoInfo())

    def testUndoSingleTransaction(self):
        view = UndoView()
        view.context = None
        view.request = TestRequest()
        id_list = ['1']
        view.action(id_list)

        testum = TestIUndoManager()
        testum.undoTransaction(id_list)

        self.checkResult(view.getUndoInfo())

    def testUndoManyTransactions(self):
        view = UndoView()
        view.context = None
        view.request = TestRequest()
        id_list = ['1','2','3']
        view.action(id_list)

        testum = TestIUndoManager()
        testum.undoTransaction(id_list)
        
        self.checkResult(view.getUndoInfo())

    def checkResult(self, info):
        for entry in info:
            self.assertEqual(entry['datetime'], u'2001 1 1  12:00:00 ')
            self.assertEqual(entry['time'], 'today')
            self.assert_(entry['user_name'] in ('bonobo', 'monkey'))
            self.assertEqual(entry['description'], 'thing'+entry['id'])

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
