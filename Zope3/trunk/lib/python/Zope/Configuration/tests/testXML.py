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
import sys, unittest
from cStringIO import StringIO

# Caution:  tempfile.NamedTemporaryFile cannot be used on Windows, because
# the tests here want to open the file more than once.  You can't do that
# with an O_TEMPORARY file on Win2K (or higher).
import tempfile

class TempFile:
    from os import remove

    def __init__(self):
        self.file = open(tempfile.mktemp(), 'w')
        self.closed = 0
    def write(self,buffer):
        self.file.write(buffer)
    def _name(self):
        return self.file.name
    name = property(_name)
    def flush(self):
        self.file.flush()
    def close(self):
        if not self.closed:
            self.file.close()
            self.remove(self.file.name)
            self.closed = 1
    def __del__(self):
        self.close()

from Zope.Configuration.xmlconfig import xmlconfig
from Zope.Configuration.xmlconfig import testxmlconfig
from Zope.Configuration.meta import InvalidDirective, BrokenDirective
from Zope.Testing.CleanUp import CleanUp

class Test(CleanUp, unittest.TestCase):

    def testInclude(self):
        file = TempFile()
        name = file.name
        file.write(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
                 <include
                     package="Zope.Configuration.tests.Contact"
                     file="contact.zcml" />
               </zopeConfigure>""")
        file.flush()
        from Zope.Configuration.xmlconfig import XMLConfig
        x = XMLConfig(name)
        x()
        file.close()

    def testIncludeAll(self):
        file = TempFile()
        name = file.name
        file.write(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
                 <include
                     package="Zope.Configuration.tests.*"
                     file="contact.zcml" />
               </zopeConfigure>""")
        file.flush()
        from Zope.Configuration.xmlconfig import XMLConfig
        x = XMLConfig(name)
        x()
        file.close()

    def testIncludeNoPackageAndIncluderNoPackage(self):
        from os.path import split
        file = TempFile()
        full_name = file.name
        file1 = TempFile()
        full_name1 = file1.name
        name1 = split(full_name1)[-1]

        file.write(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
                 <include file="%s" />
               </zopeConfigure>""" % name1)
        file.flush()
        file1.write(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
                 <include
                     package="Zope.Configuration.tests.Contact"
                     file="contact.zcml" />
               </zopeConfigure>""")
        file1.flush()
        from Zope.Configuration.xmlconfig import XMLConfig
        x = XMLConfig(full_name)
        x()

        file.close()
        file1.close()

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

def run():
    unittest.TextTestRunner().run(test_suite())

def debug():
    test_suite().debug()

def pdb():
    import pdb
    pdb.run('debug()')

if __name__=='__main__':
    if len(sys.argv) < 2:
        run()
    else:
        globals()[sys.argv[1]]()
