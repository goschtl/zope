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
$Id: test_undo.py,v 1.2 2002/12/25 14:12:44 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.app.interfaces.undo import IUndoManager
from zope.app.browser.undo import Undo
from zope.app.services.tests.placefulsetup\
           import PlacefulSetup

class TestIUndoManager:
    __implements__ = IUndoManager

    def __init__(self):
        dict1 = {'id': '1', 'user_name': 'monkey', 'description': 'thing1',
 'time': 'today'}
        dict2 = {'id': '2', 'user_name': 'monkey', 'description': 'thing2',
 'time': 'today'}
        dict3 = {'id': '3', 'user_name': 'monkey', 'description': 'thing3',
 'time': 'today'}

        self.dummy_db = [dict1, dict2, dict3]

    def getUndoInfo(self):
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
        view = Undo(None, None)

        self.assertEqual(view.getUndoInfo(), TestIUndoManager().getUndoInfo())


    def testUndoSingleTransaction(self):
        view = Undo(None, None)
        id_list = ['1']
        view.action(id_list)

        testum = TestIUndoManager()
        testum.undoTransaction(id_list)

        self.assertEqual(view.getUndoInfo(), testum.getUndoInfo())

    def testUndoManyTransactions(self):
        view = Undo(None, None)
        id_list = ['1','2','3']
        view.action(id_list)

        testum = TestIUndoManager()
        testum.undoTransaction(id_list)

        self.assertEqual(view.getUndoInfo(), testum.getUndoInfo())

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
