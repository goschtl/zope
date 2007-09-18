##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""zodbtables tests.

$Id$
"""

import unittest
from time import time

import transaction

from apelib.zodb3 import zodbtables


TEST_DATA = [
    {'name':    'Jose',
     'sex':     'm',
     'address': '101 Example St.',
     'phone':   '123-4567',
     },
    {'name':    'Maria',
     'sex':     'f',
     'address': '102 Example St.',
     },
    {'name':    'Carlos',
     'sex':     'm',
     'phone':   '987-6543',
     },
    {'name':    'Tiago',
     'sex':     'm',
     'phone':   '123-4567',
     },
    {'name':    'Ana',
     'sex':     'f',
     'phone':   '123-4567',
     },
    ]


class ZODBTableTests(unittest.TestCase):

    table_schema = zodbtables.TableSchema()
    table_schema.add('name', primary=1, indexed=1)
    table_schema.add('sex', indexed=1)
    table_schema.add('address')
    table_schema.add('phone', indexed=1)

    def setUp(self):
        self.table = table = zodbtables.Table(self.table_schema)
        for data in TEST_DATA:
            table.insert(data)

    def tearDown(self):
        transaction.get().abort()

    def test_select_by_name(self):
        # Searches by primary key
        records = self.table.select({'name': 'Jose'})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['address'], '101 Example St.')

    def test_select_by_unknown_name(self):
        # Searches by primary key
        records = self.table.select({'name': 'Joao'})
        self.assertEqual(len(records), 0)

    def test_select_by_phone(self):
        # Searches by index
        records = self.table.select({'phone': '987-6543'})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['name'], 'Carlos')

    def test_select_by_address(self):
        # Searches one-by-one
        records = self.table.select({'address': '102 Example St.'})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['name'], 'Maria')

    def test_select_males(self):
        records = self.table.select({'sex': 'm'})
        self.assertEqual(len(records), 3)

    def test_select_females(self):
        records = self.table.select({'sex': 'f'})
        self.assertEqual(len(records), 2)

    def test_select_by_name_and_sex(self):
        records = self.table.select({'name': 'Jose', 'sex': 'm'})
        self.assertEqual(len(records), 1)

    def test_select_by_name_and_incorrect_sex(self):
        records = self.table.select({'name': 'Jose', 'sex': 'f'})
        self.assertEqual(len(records), 0)

    def test_Select_By_Sex_And_Phone(self):
        # Intersects two indexes
        records = self.table.select({'phone': '123-4567', 'sex': 'm'})
        self.assertEqual(len(records), 2)

    def test_select_all(self):
        records = self.table.select({})
        self.assertEqual(len(records), 5)

    def test_insert_minimal(self):
        self.table.insert({'name': 'Edson'})

    def test_insert_duplicate(self):
        self.assertRaises(zodbtables.DuplicateError,
                          self.table.insert, {'name':'Carlos'})

    def test_insert_without_primary_key(self):
        self.assertRaises(ValueError, self.table.insert, {})

    def test_update_new_address(self):
        # Test adding a value in a non-indexed column
        self.table.update({'name': 'Carlos'}, {'address': '99 Sohcahtoa Ct.'})
        records = self.table.select({'address': '99 Sohcahtoa Ct.'})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['name'], 'Carlos')

    def test_Update_Change_Address(self):
        # Test changing a value in a non-indexed column
        self.table.update({'name': 'Jose'}, {'address': '99 Sohcahtoa Ct.'})
        records = self.table.select({'address': '99 Sohcahtoa Ct.'})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['name'], 'Jose')

    def test_update_female_addresses(self):
        # Test changing and adding simultaneously in a non-indexed column
        self.table.update({'sex': 'f'}, {'address': '99 Sohcahtoa Ct.'})
        records = self.table.select({'address': '99 Sohcahtoa Ct.'})
        self.assertEqual(len(records), 2)


    def test_update_change_phone(self):
        # Test changing a value in an indexed column
        records = self.table.select({'phone': '123-4567'})
        self.assertEqual(len(records), 3)  # Precondition

        self.table.update({'name': 'Jose'}, {'phone': '111-5555'})
        records = self.table.select({'phone': '123-4567'})
        self.assertEqual(len(records), 2)
        records = self.table.select({'phone': '111-5555'})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['name'], 'Jose')


    def test_update_change_name(self):
        # Test changing a value in a primary key column
        records = self.table.select({'name': 'Jose'})
        self.assertEqual(len(records), 1)  # Precondition

        self.table.update({'name': 'Jose'}, {'name': 'Marco'})
        records = self.table.select({'name': 'Jose'})
        self.assertEqual(len(records), 0)
        records = self.table.select({'name': 'Marco'})
        self.assertEqual(len(records), 1)


    def test_update_name_conflict(self):
        self.assertRaises(zodbtables.DuplicateError, self.table.update,
                          {'name':'Jose'}, {'name': 'Carlos'})


    def test_delete_nothing(self):
        old_count = len(self.table.select({}))
        self.assertEqual(self.table.delete({'name': 'Edson'}), 0)
        new_count = len(self.table.select({}))
        self.assert_(old_count == new_count)


    def test_delete_all(self):
        count = len(self.table.select({}))
        self.assert_(count > 0)
        self.assertEqual(self.table.delete({}), count)
        new_count = len(self.table.select({}))
        self.assert_(new_count == 0)


    def test_delete_one(self):
        # Test deletion of one row
        records = self.table.select({'name': 'Jose'})
        self.assertEqual(len(records), 1)  # Precondition
        records = self.table.select({'phone': '123-4567'})
        self.assertEqual(len(records), 3)  # Precondition

        count = self.table.delete({'name': 'Jose'})
        self.assertEqual(count, 1)
        records = self.table.select({'name': 'Jose'})
        self.assertEqual(len(records), 0)
        records = self.table.select({'phone': '123-4567'})
        self.assertEqual(len(records), 2)


    def test_delete_by_phone(self):
        records = self.table.select({'phone': '123-4567'})
        self.assertEqual(len(records), 3)  # Precondition
        
        count = self.table.delete({'phone': '123-4567'})
        self.assertEqual(count, 3)
        records = self.table.select({'phone': '123-4567'})
        self.assertEqual(len(records), 0)
        records = self.table.select({'name': 'Jose'})
        self.assertEqual(len(records), 0)

        # Make sure it didn't delete other data
        records = self.table.select({'name': 'Maria'})
        self.assertEqual(len(records), 1)

    def test_select_partial_primary_key(self):
        # Select by only one part of a primary key
        schema = zodbtables.TableSchema()
        schema.add('name', primary=1)
        schema.add('id', primary=1)
        table = zodbtables.Table(schema)
        table.insert({'name': 'joe', 'id': 1})
        table.insert({'name': 'john', 'id': 2})
        records = table.select({'name': 'joe'})
        self.assertEqual(len(records), 1)


class ZODBTableTestsWithoutPrimaryKey(ZODBTableTests):
    # Same tests but with no primary key.  The absence of a primary
    # key affects many branches of the code.
    table_schema = zodbtables.TableSchema()
    table_schema.add('name', indexed=1)
    table_schema.add('sex', indexed=1)
    table_schema.add('address')
    table_schema.add('phone', indexed=1)

    # Disabled tests
    def test_insert_without_primary_key(self):
        pass

    def test_insert_duplicate(self):
        pass

    def test_update_name_conflict(self):
        pass


if __name__ == '__main__':
    unittest.main()

