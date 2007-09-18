##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Test of storing various kinds of objects

$Id$
"""

from cStringIO import StringIO
import time
from types import ListType, TupleType

import transaction
from Acquisition import aq_base
from Persistence import Persistent
from ZODB import POSException
from Persistence import PersistentMapping
from OFS.Folder import Folder
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem
from OFS.Image import manage_addFile
from OFS.DTMLMethod import DTMLMethod
from AccessControl.User import User, UserFolder
from Products.PythonScripts.PythonScript import PythonScript
from Products.ZSQLMethods.SQL import manage_addZSQLMethod
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from DateTime import DateTime

from apelib.core.interfaces import OIDConflictError


class TestFolder(Folder):

    meta_type = 'Zope2FS Test Folder'

    def __init__(self, title):
        self.title = title


class TestObjectManager(ObjectManager):

    meta_type = 'Zope2FS Test ObjectManager'

    def __init__(self, title):
        self.title = title


class TestFile(SimpleItem):

    meta_type = 'Zope2FS Test File'

    def __init__(self, content):
        self.content = content


class FixedSchemaTestFolder(Folder):

    _properties = (
        {'id': 'mystring', 'type': 'string', 'mode': 'w'},
        {'id': 'myfloat', 'type': 'float', 'mode': 'w'},
        {'id': 'myint', 'type': 'int', 'mode': 'w'},
        {'id': 'mylong', 'type': 'long', 'mode': 'w'},
        {'id': 'mydate', 'type': 'date', 'mode': 'w'},
        {'id': 'mytext', 'type': 'text', 'mode': 'w'},
        {'id': 'myboolean0', 'type': 'boolean', 'mode': 'w'},
        {'id': 'myboolean1', 'type': 'boolean', 'mode': 'w'},
        )

    mystring = 'abc'
    myfloat = 3.14
    myint = -100
    mylong = 2L ** 40 + 10
    mydate = DateTime('2004/03/25')
    mytext = '987\n654\n321\n'
    myboolean0 = 0
    myboolean1 = 1


class Zope2TestBase:

    def test_load(self):
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            app.getId()
        finally:
            conn.close()

    def test_store(self):
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'Holidays'
            app._setObject(f.id, f, set_owner=0)
            transaction.get().commit()

            f2 = Folder()
            f2.id = 'Christmas'
            f._setObject(f2.id, f2, set_owner=0)
            transaction.get().commit()

            f3 = Folder()
            f3.id = 'Eve'
            f2._setObject(f3.id, f3, set_owner=0)
            transaction.get().commit()

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                self.assert_(hasattr(app, 'Holidays'))
                self.assert_(hasattr(app.Holidays, 'Christmas'))
                self.assert_(hasattr(app.Holidays.Christmas, 'Eve'))
                # Verify the same OID is seen in both connections.
                self.assertEqual(app.Holidays._p_oid, f._p_oid)
            finally:
                conn2.close()

        finally:
            conn.close()

    def test_anyfolder_storage(self):
        # Try to store a folderish object of an otherwise unknown class
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'Holidays'
            app._setObject(f.id, f, set_owner=0)
            transaction.get().commit()

            f2 = TestFolder("New Year's Eve")
            f2.id = 'NewYear'
            f._setObject(f2.id, f2, set_owner=0)
            transaction.get().commit()

            # Verify the object is in its own database record
            self.assertNotEqual(f2._p_oid, None)
            f2._p_changed = None
            self.assert_(f2._p_changed is None)

            # Verify the ability to load it
            conn2 = self.db.open()
            try:
                app2 = conn2.root()['Application']
                ff = app2.Holidays.NewYear
                self.assertEqual(ff.title, "New Year's Eve")
                self.assertEqual(ff.__class__, TestFolder)
            finally:
                conn2.close()
        finally:
            conn.close()


    def test_anyfolder_without_properties_storage(self):
        # Try to store a folderish object that does not implement
        # PropertyManager (tests OptionalSerializer)
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = TestObjectManager("* Holiday Calendar *")
            f.id = 'Holidays'
            app._setObject(f.id, f, set_owner=0)
            transaction.get().commit()

            # Verify the ability to load it
            conn2 = self.db.open()
            try:
                app2 = conn2.root()['Application']
                ff = app2.Holidays
                self.assertEqual(ff.title, "* Holiday Calendar *")
                self.assertEqual(ff.__class__, TestObjectManager)
            finally:
                conn2.close()
        finally:
            conn.close()


    def test_anyfile_storage(self):
        # Try to store a fileish object of an otherwise unknown class
        conn = self.db.open()
        try:
            content = 'insert wise expression here'

            app = conn.root()['Application']
            f = TestFile(content)
            f.id = 'testitem'
            app._setObject(f.id, f, set_owner=0)
            transaction.get().commit()

            # Verify the object is in its own database record
            self.assertNotEqual(f._p_oid, None)
            f._p_changed = None
            self.assert_(f._p_changed is None)

            # Verify the ability to load it
            conn2 = self.db.open()
            try:
                app2 = conn2.root()['Application']
                ff = app2.testitem
                self.assertEqual(ff.content, content)
                self.assertEqual(ff.__class__, TestFile)
            finally:
                conn2.close()
        finally:
            conn.close()


    def test_store_properties(self):
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'Holidays'
            f.title = 'Holiday Calendar'
            app._setObject(f.id, f, set_owner=0)
            transaction.get().commit()

            f._setProperty('pi', 3.14, 'float')
            f._setProperty('stuff', ['a', 'bc', 'd'], 'lines')
            transaction.get().commit()

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                self.assert_(hasattr(app, 'Holidays'))
                got = 0
                for k, v in app.Holidays.propertyItems():
                    if k == 'title':
                        got += 1
                        self.assertEqual(v, 'Holiday Calendar')
                    elif k == 'pi':
                        got += 1
                        self.assertEqual(v, 3.14)
                    elif k == 'stuff':
                        got += 1
                        self.assertEqual(tuple(v), ('a', 'bc', 'd'))
                self.assertEqual(got, 3)
            finally:
                conn2.close()

        finally:
            conn.close()


    def test_store_selection_properties(self):
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'Holidays'
            f.title = 'Holiday Calendar'
            app._setObject(f.id, f, set_owner=0)
            transaction.get().commit()

            f._setProperty('choices', ['alpha', 'omega', 'delta'], 'lines')
            f._setProperty('greek', 'choices', 'multiple selection')
            f._setProperty('hebrew', 'choices', 'selection')
            f.greek = ['alpha', 'omega']
            f.hebrew = 'alpha'
            transaction.get().commit()

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                self.assert_(hasattr(app, 'Holidays'))
                got = 0
                for k, v in app.Holidays.propertyItems():
                    if k == 'greek':
                        got += 1
                        self.assertEqual(tuple(v), ('alpha', 'omega'))
                    if k == 'hebrew':
                        got += 1
                        self.assertEqual(v, 'alpha')
                self.assertEqual(got, 2)
                # Be sure the select_variable got restored.
                dict = app.Holidays.propdict()
                self.assertEqual(dict['greek']['select_variable'], 'choices')
                self.assertEqual(dict['hebrew']['select_variable'], 'choices')
            finally:
                conn2.close()

        finally:
            conn.close()



    def test_store_property_types(self):
        # Test that Ape restores properties to the correct types.
        from DateTime import DateTime
        now = DateTime()
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'Holidays'
            app._setObject(f.id, f, set_owner=0)
            transaction.get().commit()

            f._setProperty('string1', 's', 'string')
            f._setProperty('float1', 3.14, 'float')
            f._setProperty('int1', 5, 'int')
            f._setProperty('long1', 2L**33, 'long')
            f._setProperty('date1', now, 'date')
            f._setProperty('date2', now, 'date_international')
            f._setProperty('text1', 'abc\ndef', 'text')
            f._setProperty('boolean0', 0, 'boolean')
            f._setProperty('boolean1', 1, 'boolean')
            transaction.get().commit()

            conn2 = self.db.open()
            try:
                app2 = conn2.root()['Application']
                f2 = app2.Holidays
                self.assertEqual(f2.string1, 's')
                self.assertEqual(f2.float1, 3.14)
                self.assertEqual(f2.int1, 5)
                self.assertEqual(f2.long1, 2L**33)
                self.assertEqual(f2.date1.ISO(), now.ISO())
                self.assertEqual(f2.date2.ISO(), now.ISO())
                self.assertEqual(f2.text1, 'abc\ndef')
                self.assertEqual(f2.boolean0, 0)
                self.assertEqual(f2.boolean1, 1)
            finally:
                conn2.close()

        finally:
            conn.close()


    def test_store_fixed_schema(self):
        # Test that Ape restores properties of fixed schemas correctly.
        # (This is a pretty grueling test.)
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = FixedSchemaTestFolder()
            f.id = 'Holidays'
            app._setObject(f.id, f, set_owner=0)
            transaction.get().commit()
            f.mystring = f.mystring * 2
            f.myint = f.myint * 2
            f.mylong = f.mylong * 2
            f.myfloat = f.myfloat * 2
            f.mydate = f.mydate + 1
            f.mytext = f.mytext * 2
            f.myboolean0 = not f.myboolean0
            f.myboolean1 = not f.myboolean1
            transaction.get().commit()

            conn2 = self.db.open()
            try:
                app2 = conn2.root()['Application']
                f2 = app2.Holidays
                self.assertEqual(f2.mystring, 'abcabc')
                self.assertEqual(f2.myint, -200)
                self.assertEqual(f2.mylong, 2L ** 41 + 20)
                self.assertEqual(f2.myfloat, 6.28)
                self.assertEqual(f2.mydate, DateTime('2004/03/26'))
                self.assertEqual(f2.mytext, '987\n654\n321\n987\n654\n321\n')
                self.assertEqual(f2.myboolean0, 1)
                self.assertEqual(f2.myboolean1, 0)
            finally:
                conn2.close()

        finally:
            conn.close()


    def test_store_user_folder(self):
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            if hasattr(app, 'acl_users'):
                app._delObject('acl_users')
            f = UserFolder()
            f.id = 'acl_users'
            app._setObject(f.id, f, set_owner=0)
            f._doAddUser('ned', 'abcdefg', ('Serf', 'Knight', 'King'), ())
            f._doAddUser('joe', '123', ('Geek',), ())
            transaction.get().commit()

            # Be sure ZODB sees the unmanaged persistent objects
            u = f.data['ned']
            self.assertEqual(f.data._p_oid, 'unmanaged')
            self.assertEqual(u._p_oid, 'unmanaged')

            # Make some changes
            u.roles = ('Knight', 'King')
            u.domains = ('localhost',)
            del f.data['joe']           # Test user deletion
            transaction.get().commit()

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                ff = app.acl_users
                self.assert_(aq_base(app.__allow_groups__) is aq_base(ff))
                self.assertEqual(len(ff.data), 1)
                user = ff.data['ned']
                self.assertEqual(user.name, 'ned')
                self.assertEqual(len(user.roles), 2)
                self.assert_('Knight' in user.roles)
                self.assert_('King' in user.roles)
                self.assertEqual(user.domains, ('localhost',))
                self.assert_(user is not u)
            finally:
                conn2.close()

        finally:
            conn.close()


    def test_new_object_conflict_detection(self):
        # Verify a new object won't overwrite existing objects by accident
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            app.some_attr = 'stuff'
            conn._set_serial(app, '\0' * 8)  # Pretend that it's new
            self.assertRaises(OIDConflictError, transaction.get().commit)
        finally:
            conn.close()


    def test_rename(self):
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'Holidays'
            app._setObject(f.id, f, set_owner=0)
            transaction.get().commit()

            # Do what manage_rename does, without the security checks
            ob = app.Holidays.aq_base
            app._delObject('Holidays')
            ob._setId('HolidayCalendar')
            app._setObject(ob.id, ob, set_owner=0)
            transaction.get().commit()

            self.assert_(hasattr(app, 'HolidayCalendar'))
            self.assert_(not hasattr(app, 'Holidays'))

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                self.assert_(hasattr(app, 'HolidayCalendar'))
                self.assert_(not hasattr(app, 'Holidays'))
            finally:
                conn2.close()

        finally:
            conn.close()


    def test_large_file(self):
        # Verify that 256K file objects can be serialized/deserialized.
        # Zope splits files larger than 64K into chunks.
        data = 'data' * 65536
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            manage_addFile(app, 'file', StringIO(data))
            transaction.get().commit()

            self.assertEqual(str(app.file), data)
            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                self.assertEqual(str(app.file), data)
                transaction.get().abort()
            finally:
                conn2.close()
        finally:
            conn.close()


    def test_file_preserves_content_type(self):
        # Verify that a file's content_type is preserved.
        # Note that there is some contention between content_type
        # guessing and the content_type property.
        data = (
            '\n'
            'This is not just text\n'
            'In a frivolous file test\n'
            'But a wise practice.\n'
            )
        ct = 'text/x-haiku'
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            manage_addFile(app, 'file', StringIO(data))
            app.file.content_type = ct
            transaction.get().commit()

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                self.assertEqual(app.file.content_type, ct)
            finally:
                conn2.close()
        finally:
            conn.close()


    def test_page_template(self):
        text = '<span tal:content="string:Hello">example</span>'
        expected = '<span>Hello</span>'
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            template = ZopePageTemplate('template', text)
            app._setObject(template.id, template, set_owner=0)
            transaction.get().commit()

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                res = app.template()
                self.assertEqual(res.strip(), expected)
                self.assert_(not app.template._p_changed)
            finally:
                conn2.close()

        finally:
            conn.close()


    def test_python_script(self, with_proxy_roles=0):
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            script = PythonScript('script')
            script.write('##title=test script\nreturn "OK"')
            script._makeFunction()
            app._setObject(script.id, script, set_owner=0)
            if with_proxy_roles:
                # set a proxy role and verify nothing breaks
                script._proxy_roles = ('System Administrator',)
            transaction.get().commit()

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                script = app.script
                self.assertEqual(script.title, 'test script')
                res = script()
                self.assertEqual(res, 'OK')
            finally:
                conn2.close()

        finally:
            conn.close()


    def test_python_script_with_proxy_roles(self):
        # This once failed because PythonScripts check proxy roles
        # on calls to write().
        self.test_python_script(with_proxy_roles=1)


    def test_dtml_method(self):
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            m = DTMLMethod()
            m._setId('m')
            method_body = '''All <dtml-var expr="'OK'">.'''
            m.manage_edit(method_body, 'test method')
            app._setObject(m.getId(), m, set_owner=0)
            transaction.get().commit()

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                m = app.m
                self.assertEqual(m.title, 'test method')
                res = m()
                self.assertEqual(res, 'All OK.')
            finally:
                conn2.close()

        finally:
            conn.close()


    def test_zsql_method(self):
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            template = 'SELECT <dtml-var foo> from <dtml-var bar>'
            manage_addZSQLMethod(app, 'm', 'test sql', 'none', 'foo bar',
                                 template)
            transaction.get().commit()

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                m = app.m
                self.assertEqual(m.title, 'test sql')
                self.assertEqual(m._arg._keys, ['foo', 'bar'])
                self.assertEqual(m.src, template)
            finally:
                conn2.close()

        finally:
            conn.close()


    def test_security_attributes(self):
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'Holidays'
            app._setObject(f.id, f, set_owner=0)
            f = app.Holidays
            u = UserFolder()
            u.id = 'acl_users'
            f._setObject(u.id, u, set_owner=0)
            u._doAddUser('shane', 'abcdefg', ('Elder',), ())

            f._owner = (['Holidays', 'acl_users'], 'shane')
            f.__ac_roles__ = ['Elder', 'Manager', 'Missionary']
            f.__ac_local_roles__ = {'shane': ['Missionary']}
            f._proxy_roles = ['Manager']
            f._View_Permission = ('Owner', 'Elder')
            f._Add_Folders_Permission = ['Elder']

            transaction.get().commit()

            conn2 = self.db.open()
            try:
                # Verify that loading works
                app = conn2.root()['Application']
                f2 = app.Holidays
                user = f2.getOwner()
                self.assertEqual(user.getUserName(), 'shane')
                self.assert_('Elder' in user.getRoles())
                self.assertEqual(
                    list(f2.__ac_roles__), ['Elder', 'Manager', 'Missionary'])

                roles = {}
                for role in list(user.getRolesInContext(f2)):
                    if role != 'Authenticated' and role != 'Anonymous':
                        roles[role] = 1
                self.assertEqual(roles, {'Elder':1, 'Missionary':1})
                self.assertEqual(tuple(f2._proxy_roles), ('Manager',))

                self.assert_(isinstance(f2._View_Permission, TupleType),
                             "View permission should not be acquired")
                self.assert_(isinstance(f2._Add_Folders_Permission, ListType),
                             "Add Folders permission should be acquired")
                roles = {}
                for role in list(f2._View_Permission):
                    roles[role] = 1
                self.assertEqual(roles, {'Elder':1, 'Owner':1})

                # Write some changes to verify that changes work
                f2._owner = None
                del f2._proxy_roles
                f2.__ac_roles__ += ('Teacher',)
                transaction.get().commit()
            finally:
                conn2.close()

            # Make sure the changes are seen
            conn.sync()
            self.assert_(f.getOwner() is None, f.getOwner())
            self.assert_(not hasattr(f, '_proxy_roles'))
            self.assertEqual(
                list(f.__ac_roles__),
                ['Elder', 'Manager', 'Missionary', 'Teacher'])
        finally:
            conn.close()


    def test_mod_time(self):
        # Verify _p_mtime is within a reasonable range.
        conn = self.db.open()
        try:
            now = time.time()
            app = conn.root()['Application']
            app.title = 'Testing'
            transaction.get().commit()
            self.assert_(app._p_mtime > now - 10)
            self.assert_(app._p_mtime < now + 10)
        finally:
            conn.close()


    def test_write_with_ghosts(self):
        # It should be possible to write a container even if one
        # or more of its subobjects are ghosts.
        conn = self.db.open()
        try:
            root = conn.root()
            root['foo'] = 1
            f = Folder()
            f.id = 'bar'
            root['bar'] = f
            transaction.get().commit()
            conn2 = self.db.open()
            try:
                root2 = conn2.root()
                root2['foo'] = 2
                self.assertEqual(root2['bar']._p_changed, None)
                transaction.get().commit()
            finally:
                conn2.close()
        finally:
            conn.close()


    def test_btreefolder2(self):
        from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = BTreeFolder2('Holidays')
            f.id = 'Holidays'
            app._setObject(f.id, f, set_owner=0)
            f2 = Folder()
            f2.id = 'Easter'
            app.Holidays._setObject(f2.id, f2)
            transaction.get().commit()
            # Verify serialize() found the unmanaged subobjects.
            self.assertEqual(app.Holidays._tree._p_oid, 'unmanaged')
            # Sanity check
            self.assertEqual(app.Holidays.objectCount(), 1)

            conn2 = self.db.open()
            try:
                app2 = conn2.root()['Application']
                self.assert_(app2.Holidays._tree.has_key('Easter'))
                self.assert_(not app2.Holidays.__dict__.has_key('Easter'))
                # Verify deserialize() found the unmanaged subobjects.
                self.assertEqual(app2.Holidays._tree._p_oid, 'unmanaged')
                app2.Holidays._delObject('Easter')
                transaction.get().commit()
            finally:
                conn2.close()

            # The deletion should be seen by both connections.
            conn.sync()
            self.assertEqual(app.Holidays.objectCount(), 0)

        finally:
            conn.close()


    def test_deactivate_unmanaged_persistent(self):
        # Some Zope code deactivates unmanaged persistent objects.
        # Verify that Ape can handle it.
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'Holidays'
            f.stowaway = Folder()
            f.stowaway.id = 'stowaway'
            f.stowaway._prop = 'value1'
            app._setObject(f.id, f, set_owner=0)
            transaction.get().commit()
            f.stowaway._p_deactivate()
            self.assertEqual(f.stowaway._prop, 'value1')

            # Check aborting changes to an unmanaged object.
            f.stowaway._prop = 'value2'
            self.assertEqual(f._p_changed, 1)
            transaction.get().abort()
            self.assertEqual(f.stowaway._prop, 'value1')
            self.assertEqual(f._p_changed, 0)
        finally:
            conn.close()


    def test_upo_state_after_deactivate(self):
        # An unmanaged persistent object that gets deactivated
        # and reactivated should have the most recent state.
        self.db.setCacheSize(10)  # Don't flush the objects at commit
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'Holidays'
            f.stowaway = Folder()
            f.stowaway.id = 'stowaway'
            f.stowaway._prop = 'value1'
            app._setObject(f.id, f, set_owner=0)
            transaction.get().commit()
            self.assertEqual(f._p_changed, 0)

            self.assertEqual(f.stowaway._p_oid, 'unmanaged')
            f.stowaway._prop = 'value2'
            transaction.get().commit()
            self.assertEqual(f._p_changed, 0)

            del f.stowaway._p_changed
            self.assertEqual(f.stowaway._p_changed, None)
            self.assertEqual(f.stowaway._prop, 'value2')
        finally:
            conn.close()


    def test_dcworkflow(self):
        # Verifies storing a DCWorkflow instance doesn't blow up
        try:
            from Products.DCWorkflow.Default import createDefaultWorkflowRev2
        except ImportError:
            print
            print 'Warning: Not running the DCWorkflow test'
            return
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = createDefaultWorkflowRev2('flow')
            app._setObject(f.id, f)
            transaction.get().commit()
        
            conn2 = self.db.open()
            try:
                app2 = conn2.root()['Application']
                self.assertEqual(app2.flow.states.private.getId(), 'private')
            finally:
                conn2.close()
        finally:
            conn.close()
