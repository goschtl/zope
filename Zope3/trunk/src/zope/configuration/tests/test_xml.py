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

import os.path
import sys
import tempfile
import unittest

from zope.testing.cleanup import CleanUp


# Caution:  tempfile.NamedTemporaryFile cannot be used on Windows, because
# the tests here want to open the file more than once.  You can't do that
# with an O_TEMPORARY file on Win2K (or higher).

class TempFile:
    # this actually becomes the remove() method
    from os import remove

    def __init__(self, suffix=''):
        self.file = open(tempfile.mktemp(suffix), 'w')
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


class Test(CleanUp, unittest.TestCase):

    def checkZCMLText(self, text):
        file = TempFile()
        name = file.name
        file.write(text)
        file.flush()
        from zope.configuration.xmlconfig import XMLConfig
        x = XMLConfig(name)
        x()
        file.close()

    def testInclude(self):
        self.checkZCMLText(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
                 <include
                     package="zope.configuration.tests.contact"
                     file="contact.zcml" />
               </zopeConfigure>""")

    def testIncludeAll(self):
        self.checkZCMLText(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
                 <include
                     package="zope.configuration.tests.*"
                     file="contact.zcml" />
               </zopeConfigure>""")

    def testIncludeIn(self):
        self.checkZCMLText(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
                 <include
                     package="zope.configuration.tests.contact"
                     file="alternate.zcml" />
               </zopeConfigure>""")

    def testToplevelIn(self):
        file = TempFile('.in')
        name = file.name
        assert name.endswith('.in')
        file.write(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
                 <include
                     package="zope.configuration.tests.contact"
                     file="contact.zcml" />
               </zopeConfigure>""")
        file.flush()
        from zope.configuration.xmlconfig import XMLConfig
        x = XMLConfig(name[:-3])
        x()
        file.close()

    def testIncludeNoSiteManagementFolder(self):
        file = TempFile()
        full_name = file.name
        file1 = TempFile()
        full_name1 = file1.name
        name1 = os.path.split(full_name1)[-1]

        file.write(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
                 <include file="%s" />
               </zopeConfigure>""" % name1)
        file.flush()
        file1.write(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
                 <include
                     package="zope.configuration.tests.contact"
                     file="contact.zcml" />
               </zopeConfigure>""")
        file1.flush()
        from zope.configuration.xmlconfig import XMLConfig
        x = XMLConfig(full_name)
        x()

        file.close()
        file1.close()

def test_suite():
    return unittest.makeSuite(Test)

def run():
    unittset.main(defaultTest="test_suite")

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
