##############################################################################
# 
# Zope Public License (ZPL) Version 0.9.6
# ---------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
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
# 3. Any use, including use of the Zope software to operate a website,
#    must either comply with the terms described below under
#    "Attribution" or alternatively secure a separate license from
#    Digital Creations.  Digital Creations will not unreasonably
#    deny such a separate license in the event that the request
#    explains in detail a valid reason for withholding attribution.
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
# Attribution
# 
#   Individuals or organizations using this software as a web
#   site ("the web site") must provide attribution by placing
#   the accompanying "button" on the website's main entry
#   point.  By default, the button links to a "credits page"
#   on the Digital Creations' web site. The "credits page" may
#   be copied to "the web site" in order to add other credits,
#   or keep users "on site". In that case, the "button" link
#   may be updated to point to the "on site" "credits page".
#   In cases where this placement of attribution is not
#   feasible, a separate arrangment must be concluded with
#   Digital Creations.  Those using the software for purposes
#   other than web sites must provide a corresponding
#   attribution in locations that include a copyright using a
#   manner best suited to the application environment.  Where
#   attribution is not possible, or is considered to be
#   onerous for some other reason, a request should be made to
#   Digital Creations to waive this requirement in writing.
#   As stated above, for valid requests, Digital Creations
#   will not unreasonably deny such requests.
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
'''This module implements a simple item mix-in for objects that have a
very simple (e.g. one-screen) management interface, like documents,
Aqueduct database adapters, etc.

This module can also be used as a simple template for implementing new
item types. 

$Id: SimpleItem.py,v 1.30 1999/01/22 23:12:31 amos Exp $'''
__version__='$Revision: 1.30 $'[11:-2]

import regex, sys, Globals, App.Management
from DateTime import DateTime
from CopySupport import CopySource
from string import join, lower
from types import InstanceType, StringType
import marshal

HTML=Globals.HTML

class Item(CopySource, App.Management.Tabs):
    """A simple Principia object. Not Folderish."""
    isPrincipiaFolderish=0
    isTopLevelPrincipiaApplicationObject=0

    # Name, relative to SOFTWARE_URL of icon used to display item
    # in folder listings.
    icon='Product/icon'

    # Meta type used for selecting all objects of a given type.
    meta_type='simple item'

    # Default title.  
    title=''

    manage_info   =Globals.HTMLFile('App/manage_info')
    manage_options=({'icon':'', 'label':'Manage',
                     'action':'manage_main', 'target':'manage_main',
                    },
                    {'icon':'', 'label':'Access Control',
                     'action':'manage_access', 'target':'manage_main',
                     },
                    {'icon':'', 'label':'Undo',
                     'action':'manage_UndoForm','target':'manage_main',
                     },
                    )

    def title_or_id(self):
        """
        Utility that returns the title if it is not blank and the id
        otherwise.
        """
        return self.title or self.id

    def title_and_id(self):
        """
        Utility that returns the title if it is not blank and the id
        otherwise.  If the title is not blank, then the id is included
        in parens.
        """
        t=self.title
        return t and ("%s (%s)" % (t,self.id)) or self.id
    
    def this(self):
        "Handy way to talk to ourselves in document templates."
        return self

    def tpURL(self):
        "My URL as used by tree tag"
        url=self.id
        if hasattr(url,'im_func'): url=url()
        return url

    def tpValues(self):
        "My sub-objects as used by the tree tag"
        return ()

    _manage_editedDialog=Globals.HTMLFile('editedDialog', globals())
    def manage_editedDialog(self, REQUEST, **args):
        return apply(self._manage_editedDialog,(self, REQUEST), args)

    def raise_standardErrorMessage(
        self, client=None, REQUEST={},
        error_type=None, error_value=None, tb=None,
        error_tb=None, error_message='',
        tagSearch=regex.compile('[a-zA-Z]>').search):
        try:
            if error_type  is None: error_type =sys.exc_info()[0]
            if error_value is None: error_value=sys.exc_info()[1]

            # allow for a few different traceback options
            if tb is None and error_tb is None:
                tb=sys.exc_info()[2]
            if type(tb) is not type('') and (error_tb is None):
                error_tb=pretty_tb(error_type, error_value, tb)
            elif type(tb) is type('') and not error_tb:
                error_tb=tb

            if lower(str(error_type)) in ('redirect',):
                raise error_type, error_value, tb

            if not error_message:
                if type(error_value) is InstanceType:
                    s=str(error_value)
                    if tagSearch(s) >= 0:
                        error_message=error_value
                elif (type(error_value) is StringType
                      and tagSearch(error_value) >= 0):
                    error_message=error_value

            if client is None: client=self
            if not REQUEST: REQUEST=self.aq_acquire('REQUEST')

            try:
                s=getattr(client, 'standard_error_message')
                v=HTML.__call__(s, client, REQUEST, error_type=error_type,
                                error_value=error_value,
                                error_tb=error_tb,error_traceback=error_tb,
                                error_message=error_message)
            except: v='Sorry, an error occured'
            raise error_type, v, tb
        finally:
            tb=None

    def uniqueId(self):
        return self._p_oid

    def aqObjectBind(self, ob):
        return ob.__of__(self)

    def manage(self, URL1):
        " "
        raise 'Redirect', "%s/manage_main" % URL1 

    # This keeps simple items from acquiring their parents
    # objectValues, etc., when used in simple tree tags.
    def objectValues(self, spec=None):
        return ()
    objectIds=objectItems=objectValues

    # FTP support methods
    
    def manage_FTPstat(self,REQUEST):
        "psuedo stat, used by FTP for directory listings"
        from AccessControl.User import nobody
        mode=0100000
        # check read permissions
        if hasattr(self.aq_base,'manage_FTPget'):
            if REQUEST['AUTHENTICATED_USER'].allowed(self.manage_FTPget,
                                    self.manage_FTPget.__roles__):
                mode=mode | 0440
            if nobody.allowed(self.manage_FTPget, self.manage_FTPget.__roles__):
                mode=mode | 0004
        # check write permissions
        if hasattr(self.aq_base,'PUT'):
            if REQUEST['AUTHENTICATED_USER'].allowed(self.PUT,
                                    self.PUT.__roles__):
                mode=mode | 0220
            if nobody.allowed(self.PUT, self.PUT.__roles__):
                mode=mode | 0002
        # get size
        if hasattr(self,'manage_FTPget'):
            size=len(self.manage_FTPget())
        else:
            size=0
        # get modification time
        mtime=self.bobobase_modification_time().timeTime()
        return marshal.dumps((mode,0,0,1,0,0,size,mtime,mtime,mtime))

    def manage_FTPlist(self,REQUEST):
        """Directory listing for FTP. In the case of non-Foldoid objects,
        the listing should contain one object, the object itself."""
        stat=marshal.loads(self.manage_FTPstat(REQUEST))
        return marshal.dumps((self.id,stat))


class Item_w__name__(Item):
    """Mixin class to support common name/id functions"""

    def title_or_id(self):
        """Utility that returns the title if it is not blank and the id
        otherwise."""
        return self.title or self.__name__

    def title_and_id(self):
        """Utility that returns the title if it is not blank and the id
        otherwise.  If the title is not blank, then the id is included
        in parens."""
        t=self.title
        return t and ("%s (%s)" % (t,self.__name__)) or self.__name__

    def _setId(self, id):
        self.__name__=id

def format_exception(etype,value,tb,limit=None):
    import traceback
    result=['Traceback (innermost last):']
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    n = 0
    while tb is not None and (limit is None or n < limit):
        f = tb.tb_frame
        lineno = tb.tb_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        locals=f.f_locals
        result.append('  File %s, line %d, in %s'
                      % (filename,lineno,name))
        try: result.append('    (Object: %s)' %
                           locals[co.co_varnames[0]].__name__)
        except: pass
        try: result.append('    (Info: %s)' %
                           str(locals['__traceback_info__']))
        except: pass
        tb = tb.tb_next
        n = n+1
    result.append(join(traceback.format_exception_only(etype, value),' '))
#    sys.exc_type,sys.exc_value,sys.exc_traceback=etype,value,tb
    return result

def pretty_tb(t,v,tb):
    tb=format_exception(t,v,tb,200)
    tb=join(tb,'\n')
    return tb
