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
__doc__ = """Zope version

$Id: ZopeVersion.py,v 1.2 2002/06/10 23:27:51 jim Exp $"""

from Zope.App.OFS.ApplicationControl.IZopeVersion import IZopeVersion
import os

class ZopeVersion:

    __implements__ =  IZopeVersion

    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.ApplicationControl.IZopeVersion.

    def getZopeVersion(self):
        'See Zope.App.OFS.ApplicationControl.IZopeVersion.IZopeVersion'

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
            version_id = f.read().split("\n")[0] or version_id
            
        version = "%s%s" % (version_id, version_tag)
        return version


    #
    ############################################################

ZopeVersionUtility = ZopeVersion()    
