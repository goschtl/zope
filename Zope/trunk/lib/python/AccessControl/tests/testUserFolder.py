##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""User folder tests
"""

__rcs_id__='$Id: testUserFolder.py,v 1.2 2001/10/02 16:16:25 matt Exp $'
__version__='$Revision: 1.2 $'[11:-2]

import os, sys
execfile(os.path.join(sys.path[0], 'framework.py'))

import ZODB
from DocumentTemplate import HTML
from DocumentTemplate.tests.testDTML import DTMLTests
from Products.PythonScripts.standard import DTML
from AccessControl import User, Unauthorized
from AccessControl.User import BasicUserFolder
from ExtensionClass import Base

class SecurityTests (DTMLTests):

    def testMaxListUsers(self):
        # create a folder-ish thing which contains a roleManager,
        # then put an acl_users object into the folde-ish thing

        class Folderish(BasicUserFolder):
            def __init__(self, size, count):
                self.maxlistusers = size
                self.users = []
                self.acl_users = self
                for i in xrange(count):
                    self.users.append("Nobody")
                   
            def getUsers(self):
                return self.users

            def user_names(self):
                return self.getUsers()


        tinyFolderOver = Folderish(15, 20)
        tinyFolderUnder = Folderish(15, 10)

        assert tinyFolderOver.maxlistusers == 15
        assert tinyFolderUnder.maxlistusers == 15
        assert len(tinyFolderOver.user_names()) == 20
        assert len(tinyFolderUnder.user_names()) == 10

        try:
            list = tinyFolderOver.get_valid_userids()
            assert 0, "Did not raise overflow error"
        except OverflowError:
            pass

        try:
            list = tinyFolderUnder.get_valid_userids()
            pass
        except OverflowError:
            assert 0, "Raised overflow error erroneously"



framework()
