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
"""Test of storing folders on the filesystem via ZODB

$Id$
"""

import os
import sys
from shutil import rmtree
import unittest
from tempfile import mktemp
from cStringIO import StringIO

import transaction
from OFS.Application import Application
from OFS.Image import File, manage_addImage, manage_addFile
from Products.PythonScripts.PythonScript import PythonScript
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from apelib.core.interfaces import OIDConflictError
from apelib.zodb3.db import ApeDB
from apelib.zodb3.storage import ApeStorage
from apelib.zodb3.resource import StaticResource
from apelib.zope2.mapper import load_conf
from apelib.fs.interfaces import FSWriteError
from apelib.fs.connection import FSConnection
from apelib.tests.zope2testbase import Zope2TestBase, Folder


try:
    __file__
except NameError:
    __file__ = os.path.abspath(sys.argv[0])

tmpdir = mktemp()

conf = None


class Zope2FSTests (unittest.TestCase, Zope2TestBase):

    annotation_prefix = '.'

    def setUp(self):
        self.db, self.conn = self.open_database()
        self.conf = conf
        self.path = tmpdir
        c = self.db.open()
        try:
            if not c.root().has_key('Application'):
                from OFS.Application import Application
                c.root()['Application'] = Application()
                transaction.commit()
        finally:
            c.close()
        transaction.begin()
        self.clear_caches()

    def tearDown(self):
        transaction.abort()
        if self.db is not None:
            self.db.close()
        rmtree(self.path)

    def open_database(self):
        global conf
        if conf is None:
            conf = load_conf('filesystem')
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)
        conn = FSConnection(tmpdir, annotation_prefix=self.annotation_prefix)
        conns = {'fs': conn}
        resource = StaticResource(conf)
        storage = ApeStorage(resource, conns)
        db = ApeDB(storage, resource, cache_size=0)
        return db, conn

    def clear_caches(self):
        """Clears caches after a filesystem write.
        """
        self.conn.afs.clear_cache()

    def test_classification_preservation(self):
        # Ensure that classification doesn't get forgotten.
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'Holidays'
            app._setObject(f.id, f, set_owner=0)
            transaction.commit()

            f2 = Folder()
            f2.id = 'Christmas'
            f._setObject(f2.id, f2, set_owner=0)
            transaction.commit()

            f3 = Folder()
            f3.id = 'Eve'
            f2._setObject(f3.id, f3, set_owner=0)
            transaction.commit()

            for folder in (f, f2, f3):
                text = self.conn.read_annotation(folder._p_oid, 'classification')
                self.assert_(text.find('class_name=OFS.Folder.Folder') >= 0)
        finally:
            conn.close()


    def test_ignore_mismatched_id(self):
        # Verify that FSAutoID doesn't care if the ID of an item
        # doesn't match what the folder thinks the item's ID should
        # be.
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'Holidays'
            app._setObject(f.id, f, set_owner=0)
            transaction.commit()

            ob = app.Holidays
            ob._setId('HolidayCalendar')
            transaction.commit()
        finally:
            conn.close()


    def test_reuse_path(self):
        # Verifies that ApeConnection doesn't trip over reuse of a path that's
        # no longer in use.
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'Holidays'
            app._setObject(f.id, f, set_owner=0)
            transaction.commit()

            f = None  # Forget the reference to folder
            app._delObject('Holidays')
            transaction.commit()

            f = Folder()
            f.id = 'Holidays'
            app._setObject(f.id, f, set_owner=0)
            transaction.commit()
        finally:
            conn.close()


    def test_automatic_page_template_extension(self):
        text = '<span tal:content="string:Hello">example</span>'
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            template = ZopePageTemplate('template', text)
            app._setObject(template.id, template, set_owner=0)
            transaction.commit()

            dir = self.conn.basepath
            names = os.listdir(dir)
            self.assert_('template.html' in names, names)
            self.assert_('template' not in names, names)
        finally:
            conn.close()


    def test_preserve_names_without_extensions(self):
        # Verifies that FSConnection retains original object names,
        # even though the files might be stored with extensions.
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'folder'
            app._setObject(f.id, f, set_owner=0)
            for n in range(3):
                script = PythonScript('script%d' % n)
                script.write('##title=test script\nreturn "OK"')
                f._setObject(script.id, script, set_owner=0)
            transaction.commit()

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                f = app.folder
                for n in range(3):
                    self.assert_(hasattr(f, 'script%d' % n))
                    self.assert_(not hasattr(f, 'script%d.py' % n))
                # white box test: verify the scripts were actually stored
                # with .py extensions.
                dir = os.path.join(self.conn.basepath, 'folder')
                names = os.listdir(dir)
                for n in range(3):
                    self.assert_(('script%d.py' % n) in names, names)
            finally:
                conn2.close()
        finally:
            conn.close()


    def test_preserve_names_with_extensions(self):
        # Verifies that FSConnection retains original object names
        # even though the object names already have extensions.
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'folder'
            app._setObject(f.id, f, set_owner=0)
            for n in range(3):
                script = PythonScript('script%d.py' % n)
                script.write('##title=test script\nreturn "OK"')
                f._setObject(script.id, script, set_owner=0)
            transaction.commit()

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                f = app.folder
                for n in range(3):
                    self.assert_(hasattr(f, 'script%d.py' % n))
                    self.assert_(not hasattr(f, 'script%d' % n))
                # white box test: verify the scripts were actually stored
                # with .py extensions.
                dir = os.path.join(self.conn.basepath, 'folder')
                names = os.listdir(dir)
                for n in range(3):
                    self.assert_(('script%d.py' % n) in names, names)
            finally:
                conn2.close()
        finally:
            conn.close()


    def test_auto_rename_on_extension_conflict(self):
        # When you create a Python Script called "script0", Ape adds a
        # .py extension.  If, in a second transaction, you add
        # "script0.py", Ape must rename the current "script0.py" to
        # "script0" to make room for the new "script0.py".
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'folder'
            app._setObject(f.id, f, set_owner=0)

            # Can't write to 'script0' then 'script0.py'.
            script = PythonScript('script0')
            script.write('##title=test script\nreturn "OK"')
            f._setObject(script.id, script, set_owner=0)
            transaction.commit()

            dir = os.path.join(self.conn.basepath, 'folder')
            names = os.listdir(dir)
            self.assert_(('script0.py') in names, names)
            self.assert_(('script0') not in names, names)

            # script0.py already exists, so Ape should automatically rename.
            script = PythonScript('script0.py')
            script.write('##title=test script\nreturn "Hello, world!"')
            f._setObject(script.id, script, set_owner=0)
            transaction.commit()

            # Did it write them correctly?
            text = open(os.path.join(dir, 'script0')).read()
            self.assert_(text.find('OK') > 0, text)
            self.assert_(text.find('Hello, world!') < 0, text)
            text = open(os.path.join(dir, 'script0.py')).read()
            self.assert_(text.find('OK') < 0, text)
            self.assert_(text.find('Hello, world!') > 0, text)
        finally:
            conn.close()


    def test_non_conflicting_name_extensions1(self):
        # Verifies that FSConnection can write to 'script0.py' then 'script0'
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'folder'
            app._setObject(f.id, f, set_owner=0)

            # It's OK to write to 'script0.py' then 'script0'.
            script = PythonScript('script0.py')
            script.write('##title=test script\nreturn "OK"')
            f._setObject(script.id, script, set_owner=0)
            transaction.commit()

            script = PythonScript('script0')
            script.write('##title=test script\nreturn "Hello, world!"')
            f._setObject(script.id, script, set_owner=0)
            transaction.commit()

            dir = os.path.join(self.conn.basepath, 'folder')
            names = os.listdir(dir)
            self.assert_(('script0.py') in names, names)
            self.assert_(('script0') in names, names)

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                f = app.folder
                self.assertEqual(f['script0.py'](), 'OK')
                self.assertEqual(f['script0'](), 'Hello, world!')
            finally:
                conn2.close()
        finally:
            conn.close()


    def test_non_conflicting_name_extensions2(self):
        # Verifies that FSConnection can write to 'script0.py' and 'script0'
        # at the same time
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'folder'
            app._setObject(f.id, f, set_owner=0)

            # It's OK to write to 'script0.py' then 'script0'.
            script = PythonScript('script0.py')
            script.write('##title=test script\nreturn "OK"')
            f._setObject(script.id, script, set_owner=0)
            script = PythonScript('script0')
            script.write('##title=test script\nreturn "Hello, world!"')
            f._setObject(script.id, script, set_owner=0)
            transaction.commit()

            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                f = app.folder
                self.assertEqual(f['script0.py'](), 'OK')
                self.assertEqual(f['script0'](), 'Hello, world!')
            finally:
                conn2.close()
        finally:
            conn.close()


    def test_non_conflicting_name_extensions3(self):
        # Verifies that FSConnection can write to 'script0.py'
        # then 'script0.dtml', then 'script0'.
        # Then verifies that removal of items works correctly.
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'folder'
            app._setObject(f.id, f, set_owner=0)

            script = PythonScript('script0.py')
            script.write('##title=test script\nreturn "OK"')
            f._setObject(script.id, script, set_owner=0)
            transaction.commit()

            script = PythonScript('script0.dtml')
            script.write('##title=test script\nreturn "No DTML here"')
            f._setObject(script.id, script, set_owner=0)
            transaction.commit()

            script = PythonScript('script0')
            script.write('##title=test script\nreturn "Hello, world!"')
            f._setObject(script.id, script, set_owner=0)
            transaction.commit()

            dir = os.path.join(self.conn.basepath, 'folder')
            names = os.listdir(dir)
            self.assert_(('script0.py') in names, names)
            self.assert_(('script0.dtml') in names, names)
            self.assert_(('script0') in names, names)

            conn2 = self.db.open()
            try:
                app2 = conn2.root()['Application']
                f2 = app2.folder
                self.assertEqual(f2['script0.py'](), 'OK')
                self.assertEqual(f2['script0.dtml'](), 'No DTML here')
                self.assertEqual(f2['script0'](), 'Hello, world!')
            finally:
                transaction.abort()
                conn2.close()

            f._delObject('script0.py')
            transaction.commit()
            names = os.listdir(dir)
            self.assert_(('script0.py') not in names, names)
            self.assert_(('script0.dtml') in names, names)
            self.assert_(('script0') in names, names)

            f._delObject('script0')
            transaction.commit()
            names = os.listdir(dir)
            self.assert_(('script0.py') not in names, names)
            self.assert_(('script0.dtml') in names, names)
            self.assert_(('script0') not in names, names)

            script = PythonScript('script0')
            script.write('##title=test script\nreturn "Hello, world!"')
            f._setObject(script.id, script, set_owner=0)
            transaction.commit()
            names = os.listdir(dir)
            self.assert_(('script0.py') not in names, names)
            self.assert_(('script0.dtml') in names, names)
            self.assert_(('script0') in names, names)

            f._delObject('script0.dtml')
            transaction.commit()
            names = os.listdir(dir)
            self.assert_(('script0.py') not in names, names)
            self.assert_(('script0.dtml') not in names, names)
            self.assert_(('script0') in names, names)
        finally:
            conn.close()


    def test_image_extension(self):
        # Verify that a new image is stored with the correct extension.
        path = os.path.join(os.path.dirname(__file__), 'correct.png')
        f = open(path, 'rb')
        try:
            data = f.read()
        finally:
            f.close()
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            manage_addImage(app, 'image', StringIO(data))
            transaction.commit()

            self.assertEqual(app.image.data, data)
            conn2 = self.db.open()
            try:
                app = conn2.root()['Application']
                self.assertEqual(app.image.data, data)
            finally:
                conn2.close()

            dir = self.conn.basepath
            names = os.listdir(dir)
            self.assert_(('image.png') in names, names)
            self.assert_(('image') not in names, names)
        finally:
            conn.close()


    def test_corrected_file_extension(self):
        # Verify that certain content_types use the correct filename
        # extension.
        data = 'Hello, world!'
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            manage_addFile(app, 'hello', StringIO(data),
                           content_type='text/plain')
            manage_addFile(app, 'world.dat', StringIO(data),
                           content_type='text/plain')
            manage_addFile(app, 'binary_file', StringIO(data),
                           content_type='application/octet-stream')
            transaction.commit()

            dir = self.conn.basepath
            names = os.listdir(dir)
            self.assert_(('hello.txt') in names, names)
            self.assert_(('world.dat') in names, names)
            self.assert_(('hello') not in names, names)
            self.assert_(('binary_file') in names, names)
        finally:
            conn.close()


    def test_guess_type_based_on_extension(self):
        # Verify Zope chooses the right object type for
        # a new object.
        # White box test.
        dir = self.conn.basepath
        f = open(os.path.join(dir, 'test.py'), 'wt')
        f.write('return "Ok!"')
        f.close()
        self.clear_caches()
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            self.assert_(hasattr(app, 'test.py'))
            self.assert_(isinstance(app['test.py'], PythonScript))
            self.assertEqual(app['test.py'](), 'Ok!')
        finally:
            conn.close()


    def test_guess_type_with_chopped_extension(self):
        # Verify that even though the extension gets stripped off
        # in Zope, Zope still sees the object as it should.
        # White box test.
        dir = self.conn.basepath
        f = open(os.path.join(dir, 'test.py'), 'wt')
        f.write('return "Ok!"')
        f.close()

        f = open(os.path.join(dir, self.conn.afs.annotation_prefix
                              + 'properties'), 'wt')
        f.write('[object_names]\ntest\n')
        f.close()
        self.clear_caches()
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            self.assert_(hasattr(app, 'test'))
            self.assert_(isinstance(app.test, PythonScript))
            self.assertEqual(app.test(), 'Ok!')
        finally:
            conn.close()


    def test_fallback_to_file(self):
        # Verify Zope uses a File object for unrecognized files on
        # the filesystem.  White box test.
        data = 'data goes here'
        dir = self.conn.basepath
        f = open(os.path.join(dir, 'test'), 'wt')
        f.write(data)
        f.close()
        self.clear_caches()
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            self.assert_(hasattr(app, 'test'))
            self.assert_(isinstance(app['test'], File))
            self.assertEqual(str(app['test']), data)
        finally:
            conn.close()


    def test_default_property_schema(self):
        # Verify Zope uses the default property schema when no properties
        # are set.
        dir = self.conn.basepath
        os.mkdir(os.path.join(dir, 'test'))
        self.clear_caches()
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            self.assert_(hasattr(app, 'test'))
            self.assert_(isinstance(app['test'], Folder))
            self.assertEqual(app['test'].title, '')
            props = app['test']._properties
            for p in props:
                if p['id'] == 'title':
                    break
            else:
                self.fail('No title property found')
        finally:
            conn.close()


    def test_remainder_storage(self):
        # Verify that FSConnection puts the remainder in the properties file
        conn = self.db.open()
        try:
            content = 'tacked_on_data'
            app = conn.root()['Application']
            app._stowaway = content
            transaction.commit()

            # Verify the ability to load it
            conn2 = self.db.open()
            try:
                app2 = conn2.root()['Application']
                self.assertEqual(app2._stowaway, content)
            finally:
                conn2.close()

            # Verify the stowaway is in the properties file.
            dir = self.conn.basepath
            p = os.path.join(
                dir, self.conn.afs.annotation_prefix + 'properties')
            f = open(p, 'rt')
            data = f.read()
            f.close()
            self.assert_(data.find('_stowaway') >= 0)
        finally:
            conn.close()


    def test_dotted_names(self):
        # FSConnection should allow dotted names that don't look like
        # property or remainder files.
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = '.Holidays'
            app._setObject(f.id, f, set_owner=0)
            f2 = Folder()
            f2.id = '.Holidays.properties.dat'
            app._setObject(f2.id, f2, set_owner=0)
            transaction.commit()
        finally:
            conn.close()


    def test_guess_file_content_type(self):
        # Verify that file content type guessing happens.
        data = '<html><body>Cool stuff</body></html>'
        dir = self.conn.basepath
        f = open(os.path.join(dir, 'testobj'), 'wt')
        f.write(data)
        f.close()

        conn = self.db.open()
        try:
            app = conn.root()['Application']
            self.assert_(hasattr(app, 'testobj'))
            self.assertEqual(app.testobj.content_type, 'text/html')
        finally:
            conn.close()


    def test_write_to_root(self):
        # Verify it's possible to write to the _root object as well as
        # the Application object without either one stomping on each
        # other's data.
        conn = self.db.open()
        conn2 = None
        try:
            root = conn.root()
            app = root['Application']
            root['foo'] = Folder()
            root['foo'].id = 'foo'
            app.bar = Folder('bar')
            app.bar.id = 'bar'
            transaction.commit()

            conn2 = self.db.open()
            root = conn2.root()
            app = root['Application']
            self.assert_(root.has_key('foo'))
            self.assert_(hasattr(app, 'bar'))
        finally:
            conn.close()
            if conn2 is not None:
                conn2.close()


    def test_open_existing(self):
        # Verifies that opening an existing database finds the same
        # data.
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            app.test_attribute = '123'
            transaction.commit()
        finally:
            conn.close()

        # Close the database and open a new one pointing at the same
        # directory.
        self.db.close()
        self.db = None
        self.db, self.conn = self.open_database()
        conn = self.db.open()
        try:
            root = conn.root()
            app = root['Application']
            self.assertEqual(app.test_attribute, '123')
        finally:
            conn.close()


    def test_no_clobber_on_open(self):
        # Opening a database with no "_root" shouldn't clobber the
        # existing contents.
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'bar'
            app._setObject(f.id, f)
            transaction.commit()
        finally:
            conn.close()
        self.db.close()
        self.db = None

        # Destroy the _root and the annotations at the app root.
        basepath = self.conn.basepath
        root_p = os.path.join(basepath, '_root')
        if os.path.exists(root_p):
            rmtree(root_p)
        paths = self.conn.afs.get_annotation_paths(basepath)
        for path in paths:
            if os.path.exists(path):
                os.remove(path)

        # Now look for the 'bar' folder.
        self.db, self.conn = self.open_database()
        conn = self.db.open()
        try:
            root = conn.root()
            app = root['Application']
            self.assertEqual(app.bar.id, 'bar')
        finally:
            conn.close()

    def test_start_with_empty_database(self):
        # A new database should not have an Application.
        # Destroy the _root and the annotations at the app root.
        self.db.close()
        self.db = None
        basepath = self.conn.basepath
        rmtree(basepath)
        os.mkdir(basepath)
        self.db, self.conn = self.open_database()
        conn = self.db.open()
        try:
            root = conn.root()
            self.assert_(not root.has_key('Application'))
        finally:
            conn.close()

    def test_store_unlinked(self):
        # Storing an object not linked to any parents
        # shouldn't cause problems.
        conn = self.db.open()
        try:
            app = conn.root()['Application']
            f = Folder()
            f.id = 'bar'
            app._setObject(f.id, f)
            transaction.savepoint(True)
            app._delObject(f.id)
            transaction.commit()
        finally:
            conn.close()



class Zope2FSUnderscoreTests (Zope2FSTests):
    annotation_prefix = '_'


if __name__ == '__main__':
    unittest.main()

