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


import re, unittest, cStringIO
import ZPublisher, ResultObject


class SecurityBase(unittest.TestCase) :
    """ Base class for all security tests 
    $Id: SecurityBase.py,v 1.4 2001/10/18 14:30:51 andreasjung Exp $
    """

    status_regex = re.compile("Status: ([0-9]{1,4}) (.*)",re.I)\


    ################################################################
    # print the object hierachy
    ################################################################

    def _testHierarchy(self):
        """ print all test objects, permissions and roles """
        self._PrintTestEnvironment(root=self.root.test)


    def _PrintTestEnvironment(self,root):
        """ print recursive all objects """

        print '....'*len(root.getPhysicalPath()),root.getId()

        folderObjs = []

        for id,obj in root.objectItems():

            if obj.meta_type in ['Folder','TestFolder']:
                folderObjs.append(obj)

            else:                
                print '    '*(1+len(root.getPhysicalPath())),obj.getId(),
                print getattr(obj,"__roles__",(None,))

        for folder in folderObjs:
            self._PrintTestEnvironment(folder)


    ################################################################
    # Check functions for permissions, roles and friends
    ################################################################

    def _checkPermission(self, user, hier, perm, expected):
        """ permission check on an objects for a given user.

           -- 'user' is a user object as returned from a user folder
 
           -- 'hier' is the path to the object in the notation 'f1.f2.f3.obj'
            
           -- 'perm' is a permission name
        
           -- 'expected' is either 0 or 1
        """

        s = "self.root.%s" % hier
        obj = eval(s)

        res = user.has_permission(perm,obj)

        if res != expected:        
            raise AssertionError, \
                self._perm_debug (s,perm,res,expected)


    def _checkRoles(self,hier,expected_roles=()):
        """ check roles for a given object.

           -- 'hier' is the path to the object in the notation 'f1.f2.f3.obj'

           -- 'expected_roles' is a sequence of expected roles

        """
        
        s = "self.root.%s.__roles__" % hier
        roles = eval(s)

        if roles==None or len(roles)==0: 
            roles=()
        
        roles = list(roles)
        roles.sort()

        expected_roles = list(expected_roles)
        expected_roles.sort()

        if roles != expected_roles: 
            raise AssertionError, self._roles_debug(hier,roles,expected_roles)
    
    def _checkRequest(self,*args,**kw):
        """ perform a ZPublisher request """
        

        expected_code = kw.get('expected',200)
        del kw['expected']
        res = apply(self._request,args,kw)

        if expected_code != res.code:
           raise AssertionError, \
              self._request_debug(res,expected_code,args,kw) 


    ################################################################
    # Debugging helpers when raising AssertionError
    ################################################################

    def _perm_debug(self, obj , perm, res, expected):
        s+= 'Object: %s' % obj
        s+= ', Permission: %s' % perm 
        s+= ', has permission: %s' % res 
        s+= ', expected: %s' % expected

        return s
        

    def _roles_debug(self,hier,got_roles,expected_roles):

        s = 'Object: %s' % hier
        s+= ', has roles: %s ' % got_roles        
        s+= ', expected roles: %s' % expected_roles

        return s


    def _request_debug(self,res,expected,args,kw):
        
        s = 'Args: %s' % str(args)        
        s+= ', KW: %s' % str(kw)
        s+= '\n%s\n' % res.__str__(with_output=0,expected=expected)

        return s
 

    def _request(self,*args,**kw):
        """ perform a Zope request """

        io =cStringIO.StringIO()
        kw['fp']=io
        ZPublisher.Zope(*args,**kw)
        outp = io.getvalue()
        mo = self.status_regex.search(outp)

        code,txt = mo.groups()

        res = ResultObject.ResultObject()
        res.request     = args
        res.user        = kw.get('u','')
        res.code        = int(code)
        res.return_text = txt
        res.output      = outp

        return res
