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
$Id: testZopeVersion.py,v 1.2 2002/06/10 23:27:54 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Interface.Verify import verifyObject

from Zope.App.OFS.ApplicationControl.IZopeVersion import IZopeVersion
from Zope.App.OFS.ApplicationControl.ZopeVersion import ZopeVersion
import os


#############################################################################
# If your tests change any global registries, then uncomment the
# following import and include CleanUp as a base class of your
# test. It provides a setUp and tearDown that clear global data that
# has registered with the test cleanup framework.  Don't use this
# tests outside the Zope package.

# from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

#############################################################################

class Test(TestCase):
    
    def _Test__new(self):
        return ZopeVersion()
        
    def _getZopeVersion(self):
        """example zope version implementation
        """
        version_id = "Development/Unknown"
        version_tag = ""
        is_cvs = 0
        
        import Zope
        zopedir = os.path.dirname(Zope.__file__)
        
        # is this a CVS checkout?
        cvsdir = os.path.join(zopedir, "CVS" )
        if os.path.isdir(cvsdir):
            is_cvs = 1
            tagfile = os.path.join(cvsdir, "Tag")
            
            # get the tag information
            if os.path.isfile(tagfile):
                f = open(tagfile)
                tag = f.read()
                if tag.startswith("T"):
                    version_tag = " (%s)" % tag[1:-1]
        
        # try to get official Zope release information
        versionfile = os.path.join(zopedir, "version.txt")
        if os.path.isfile(versionfile) and not is_cvs:
            f = open(versionfile)
            version_id = f.read().split("\n")[0]
            
        version = "%s%s" % (version_id, version_tag)
        return version

    def test_IVerify(self):
        verifyObject(IZopeVersion, self._Test__new())

    def test_ZopeVersion(self):
        zope_version = self._Test__new()
        self.assertEqual(zope_version.getZopeVersion(), self._getZopeVersion())

        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
