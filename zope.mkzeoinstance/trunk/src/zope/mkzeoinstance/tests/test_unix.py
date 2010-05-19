##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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

import sys
import unittest
import tempfile
import os
import shutil
import cStringIO

from zope.mkzeoinstance import ZEOInstanceBuilder


class ZeoInstanceParamsTest(unittest.TestCase):

    def test_get_params(self):
        builder = ZEOInstanceBuilder()

        params = builder.get_params(zodb3_home='',
                                    zdaemon_home='',
                                    instance_home='',
                                    address='')
        expected_params = {'PACKAGE': 'ZEO',
                           'python': sys.executable,
                           'package': 'zeo',
                           'zdaemon_home': '',
                           'instance_home': '',
                           'address': '',
                           'zodb3_home': ''}

        self.assertEqual(params, expected_params)


class ZeoInstanceCreateTest(unittest.TestCase):

    def setUp(self):
        self.builder = ZEOInstanceBuilder()
        self.temp_dir = tempfile.mkdtemp()

        self.instance_home = os.path.join(self.temp_dir, 'instance')

        import zdaemon
        zdaemon_home = os.path.split(zdaemon.__path__[0])[0]

        zodb3_home = None
        for entry in sys.path:
            if os.path.exists(os.path.join(entry, 'ZODB')):
                zodb3_home = entry
                break

        self.params = {'PACKAGE': 'ZEO',
                       'python': sys.executable,
                       'package': 'zeo',
                       'zdaemon_home': zdaemon_home,
                       'instance_home': self.instance_home,
                       'address': '99999',
                       'zodb3_home': zodb3_home}

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        
    def test_create_folders_and_files(self):
        instance_home = self.instance_home
        orig_stdout = sys.stdout

        temp_out_file = cStringIO.StringIO()
        sys.stdout = temp_out_file
        self.builder.create(instance_home, self.params)
        sys.stdout = orig_stdout

        expected_out = """Created directory %(instance_home)s
Created directory %(instance_home)s/etc
Created directory %(instance_home)s/var
Created directory %(instance_home)s/log
Created directory %(instance_home)s/bin
Wrote file %(instance_home)s/etc/zeo.conf
Wrote file %(instance_home)s/bin/zeoctl
Changed mode for %(instance_home)s/bin/zeoctl to 755
Wrote file %(instance_home)s/bin/runzeo
Changed mode for %(instance_home)s/bin/runzeo to 755
""" % {'instance_home':
           instance_home}

        self.assertEqual(temp_out_file.getvalue(), expected_out)

        self.assertTrue(os.path.exists(os.path.join(instance_home, 'etc')))
        self.assertTrue(os.path.exists(os.path.join(instance_home, 'var')))
        self.assertTrue(os.path.exists(os.path.join(instance_home, 'log')))
        self.assertTrue(os.path.exists(os.path.join(instance_home, 'bin')))
        self.assertTrue(os.path.exists(os.path.join(instance_home, 'etc', 'zeo.conf')))
        self.assertTrue(os.path.exists(os.path.join(instance_home, 'bin', 'zeoctl')))
        self.assertTrue(os.path.exists(os.path.join(instance_home, 'bin', 'runzeo')))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZeoInstanceParamsTest))
    suite.addTest(unittest.makeSuite(ZeoInstanceCreateTest))
    return suite
