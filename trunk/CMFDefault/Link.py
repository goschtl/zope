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
"""
"""

ADD_CONTENT_PERMISSION = 'Add portal content'

import Globals
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.PortalContent import PortalContent
from DublinCore import DefaultDublinCoreImpl

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.CMFCore.utils import keywordsplitter
from utils import parseHeadersBody

factory_type_information = ( { 'id'             : 'Link'
                             , 'meta_type'      : 'Link'
                             , 'description'    : """\
Link items are URLs that come with additional information."""
                             , 'icon'           : 'link_icon.gif'
                             , 'product'        : 'CMFDefault'
                             , 'factory'        : 'addLink'
                             , 'immediate_view' : 'metadata_edit_form'
                             , 'actions'        :
                                ( { 'name'          : 'View'
                                  , 'action'        : 'link_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'name'          : 'Edit'
                                  , 'action'        : 'link_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                )
                             }
                           ,
                           )


def addLink( self
           , id
           , title=''
           , remote_url=''
           , description=''
           ):
    """
    Add a Link
    """
    o=Link( id, title, remote_url, description )
    self._setObject(id,o)


class Link( PortalContent
          , DefaultDublinCoreImpl
          ):
    """
        A Link
    """

    __implements__ = ( PortalContent.__implements__
                     , DefaultDublinCoreImpl.__implements__
                     )

    meta_type='Link'
    effective_date = expiration_date = None
    _isDiscussable = 1

    __ac_permissions__=(
        (CMFCorePermissions.View, ('', 'view', 'getRemoteUrl')),
        (CMFCorePermissions.ModifyPortalContent, ('edit',)),
        )

    security = ClassSecurityInfo()

    def __init__( self
                , id
                , title=''
                , remote_url=''
                , description=''
                ):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.title=title
        self.remote_url=remote_url
        self.description=description

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'edit')
    def edit( self, remote_url ):
        """
            Edit the Link
        """
        self.remote_url=remote_url
    edit = WorkflowAction(edit)

    security.declareProtected( CMFCorePermissions.View, 'SearchableText' )
    def SearchableText(self):
        """
            text for indexing
        """
        return "%s %s" % (self.title, self.description)

    security.declareProtected( CMFCorePermissions.View, 'getRemoteUrl' )
    def getRemoteUrl(self):
        """
            returns the remote URL of the Link
        """
        return self.remote_url

    def _writeFromPUT( self, body ):

        headers = {}
        headers, body = parseHeadersBody(body, headers)
        self.edit(body)

        headers['Format'] = 'text/url'
        new_subject = keywordsplitter(headers)
        headers['Subject'] = new_subject or self.Subject()
        haveheader = headers.has_key
        for key, value in self.getMetadataHeaders():
            if key != 'Format' and not haveheader(key):
                headers[key] = value
        
        self.editMetadata(title=headers['Title'],
                          subject=headers['Subject'],
                          description=headers['Description'],
                          contributors=headers['Contributors'],
                          effective_date=headers['Effective_date'],
                          expiration_date=headers['Expiration_date'],
                          format=headers['Format'],
                          language=headers['Language'],
                          rights=headers['Rights'],
                          )
        
    ## FTP handlers
    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """
            Handle HTTP (and presumably FTP?) PUT requests.
        """
        self.dav__init(REQUEST, RESPONSE)
        body = REQUEST.get('BODY', '')
        self._writeFromPUT( body )
        RESPONSE.setStatus(204)
        return RESPONSE

    security.declareProtected( CMFCorePermissions.View, 'manage_FTPget' )
    def manage_FTPget(self):
        "Get the link as text for FTP download (also used for the WebDAV SRC)"
        join = string.join
        lower = string.lower
        hdrlist = self.getMetadataHeaders()
        hdrtext = join( map( lambda x: '%s: %s' % ( x[0], x[1] )
                           , hdrlist), '\n' )
        bodytext = '%s\n\n%s' % ( hdrtext, self.getRemoteUrl() )

        return bodytext

    security.declareProtected( CMFCorePermissions.View, 'get_size' )
    def get_size( self ):
        """ Used for FTP and apparently the ZMI now too """
        return len(self.manage_FTPget())

InitializeClass( Link )

