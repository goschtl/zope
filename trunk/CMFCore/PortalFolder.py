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
    Portal folders organize content.
"""
ADD_FOLDERS_PERMISSION = 'Add portal folders'
ADD_CONTENT_PERMISSION = 'Add portal content'

import Globals, re, base64, marshal, string
import CMFCorePermissions

from CMFCorePermissions import AddPortalFolders, AddPortalContent, View
from OFS.Folder import Folder
from OFS.ObjectManager import REPLACEABLE
from Globals import HTMLFile
from AccessControl import getSecurityManager, ClassSecurityInfo
from Acquisition import aq_parent, aq_inner, aq_base
from DynamicType import DynamicType
from utils import getToolByName

#
#   HACK! HACK! HACK! HACK! HACK! HACK! HACK! HACK! HACK!
#
#   This registry needs to go away, and be replaced by a web-configurable,
#   instance-specific 'portal_types' tool.
#
_mime_type_registry = {}

def addPortalTypeHandler( MIMEType, klass ):
    """
        Set up a mapping from 'MIMEType' to 'klass', so that
        PortalFolder.PUT_factory knows what to make.  'klass' should be
        either an actual class object, whose __init__() takes no paramters
        (except 'self'), or a function taking no paramters.
    """
    _mime_type_registry[ MIMEType ] = klass

class PortalFolder( Folder, DynamicType ):
    """
        Implements portal content management, but not UI details.
    """
    meta_type = 'Portal Folder'
    portal_type = 'Folder'

    security = ClassSecurityInfo()

    

    #
    #   Each module defining a PortalContent derivative registers here.
    #
    FOLDER_ACTION = 'manage_addProduct/CMFCore/manage_addPortalFolderForm'
    content_meta_types = ( { 'name'         : 'Portal Folder'
                           , 'action'       : FOLDER_ACTION
                           , 'permission'   : 'Add portal folders'
                           }
                         ,
                         )

    def __init__( self, id, title='' ):
        self.id = id
        self.title = title

    def all_meta_types( self ):
        names = {}
        types = []

        for cmt in self.content_meta_types:
            names[ cmt[ 'name' ] ] = 1
            types.append( cmt )

        superTypes = PortalFolder.inheritedAttribute(
            'all_meta_types' )( self )

        for smt in superTypes:
            if not names.has_key( smt[ 'name' ] ):
                names[ smt[ 'name' ] ] = 1
                types.append( smt )

        return tuple( types )

    security.declareProtected(CMFCorePermissions.ManageProperties, 'edit')
    def edit(self, title=''):
        """
        Edit the folder title (and possibly other attributes later)
        """
        self.title = title

    security.declarePublic('allowedContentTypes')
    def allowedContentTypes( self ):
        """
            List type info objects for types which can be added in
            this folder.
        """
        result = []
        portal_types = getToolByName(self, 'portal_types')
        myType = portal_types.getTypeInfo(self.Type())

        if myType is not None:
            for contentType in portal_types.listTypeInfo():
                if myType.allowType(contentType.Type()):
                    result.append(contentType)
        else:
            result = portal_types.listTypeInfo()

        return result
    
    security.declareProtected(AddPortalFolders, 'manage_addPortalFolder')
    def manage_addPortalFolder(self, id, title='', REQUEST=None):
        """Add a new PortalFolder object with id *id*.
        """
        ob=PortalFolder(id, title)
        self._setObject(id, ob)
        if REQUEST is not None:
            return self.folder_contents(
                self, REQUEST, portal_status_message="Folder added")
    

    security.declarePublic('getIcon')
    def getIcon(self):
        """
          Return the correct icon file
        """
        return getattr(self, 'icon', '/misc_/OFSP/Folder_icon.gif')

    security.declarePublic('listContentTypes')
    def listContentTypes(self):
        """
           List all registered portal content types.
        """
        mtSet = {}
        for info in getToolByName(self, 'portal_types').listTypeInfo():
            mtSet[info.Metatype()] = 1
        return mtSet.keys()

    def _morphSpec(self, spec):
        new_spec = []
        types = self.listContentTypes()
        if spec is not None:
            if type(spec) == type(''):
                spec = [spec]
            for meta_type in spec:
                if not meta_type in types:
                    raise 'PortalFolderError', ('%s is not a content type'
                                                 % meta_type )
                new_spec.append(meta_type)
        return new_spec or types
    
    def _filteredItems( self, ids, kw, REQUEST=None ):
        """
            Use 'kw' as filter on child objects indicated by 'ids',
            returning a sequence of ( id, obj ) tuples.
        """
        if REQUEST is not None:
            for key,value in REQUEST.items():
                if not kw.has_key(key):
                    kw[key] = value
        query = apply( ContentFilter, (), kw )
        result = []
        append = result.append
        get = self._getOb
        for id in ids:
            obj = get( id )
            if ((hasattr(obj, 'Type') and obj.Type() == 'Portal Folder'
                 and not REQUEST.get('FilterIncludesFolders', 0))
                or query( obj )):
                append( ( id, obj ) )
        return result

    security.declarePublic('contentIds')
    def contentIds( self, spec=None, REQUEST=None, **kw ):
        """
            Provide a filtered view onto 'objectIds', allowing only
            PortalFolders and PortalContent-derivatives to show through.

            If 'kw' passed, use them to filter the results further,
            qua the standard Zope filter interface.
        """
        spec = self._morphSpec( spec )
        ids = self.objectIds( spec )

        if not kw and not REQUEST:
            return ids
        
        return map( lambda item: item[0],
                    self._filteredItems( ids, kw, REQUEST ) )

    security.declarePublic('contentValues')
    def contentValues( self, spec=None, REQUEST=None, **kw ):
        """
            Provide a filtered view onto 'objectValues', allowing only
            PortalFolders and PortalContent-derivatives to show through.
        """
        spec = self._morphSpec( spec )
        if not kw and not REQUEST:
            return self.objectValues( spec )

        ids = self.objectIds( spec )
        return map( lambda item: item[1],
                    self._filteredItems( ids, kw, REQUEST ) )

    security.declarePublic('contentItems')
    def contentItems( self, spec=None, REQUEST=None, **kw ):
        """
            Provide a filtered view onto 'objectItems', allowing only
            PortalFolders and PortalContent-derivatives to show through.
        """
        spec = self._morphSpec( spec )
        if not kw and not REQUEST:
            return self.objectItems( spec )

        ids = self.objectIds( spec )
        return self._filteredItems( ids, kw, REQUEST )

    security.declareProtected(View, 'Type')
    def Type( self ):
        """
             Implement dublin core type
        """
        return self.meta_type

    def createFilterString( self, decoded ):
        """
            Build Filter string for cookie munging from the REQUEST variables.
        """
        encoded = string.strip(base64.encodestring( marshal.dumps( decoded )))
        encoded = string.join(string.split(encoded, '\n'), '')
        return encoded

    security.declarePublic('parseFilterString')
    def parseFilterString( self, REQUEST=None ):
        """
            Parse cookie string for using variables in dtml.
        """
        if REQUEST is None:
			REQUEST = {}
        # Set up defaults.
        decoded = { 'open': 0
                  , 'Subject': ''
                  , 'Type': []
                  }
        # Parse the cookie
        if REQUEST.has_key('folderfilter'):
            decoded.update(marshal.loads(
                base64.decodestring(REQUEST['folderfilter'])))
        # Update the REQUEST (only if it doesn't have the key!).
        for key in ( 'open', 'Subject', 'Type' ):
            if REQUEST.has_key( key ) and (
                type(REQUEST[key]) in [type(""), type([]), type(1)]):
                decoded[ key ] = REQUEST[ key ]
            else:
                REQUEST[ key ] = decoded[ key ]
        # Make the cookie.
        REQUEST['encoded'] = self.createFilterString(decoded)

    def PUT_factory( self, name, typ, body ):
        """
            Dispatcher for PUT requests to non-existent IDs.  Returns
            an object of the appropriate type (or None, if we don't
            know what to do).
        """
        klass = _mime_type_registry.get( typ, None )
        if klass is None:
            return None
        obj = klass(id=name)
        return obj

    security.declareProtected(AddPortalContent, 'invokeFactory')
    def invokeFactory(self, type_name, id, RESPONSE=None):
        '''
        Invokes the portal_types tool.
        '''
        pt = getToolByName(self, 'portal_types')
        pt.constructContent(type_name, self, id, RESPONSE)

    def _checkId(self, id, allow_dup=0):
        PortalFolder.inheritedAttribute('_checkId')(self, id, allow_dup)
        
        # This method prevents people other than the portal manager
        # from overriding skinned names.
        if not allow_dup:
            if not getSecurityManager().checkPermission(
                'Manage portal', self):
                ob = self
                while ob is not None and not getattr(ob, '_isPortalRoot', 0):
                    ob = aq_parent(aq_inner(ob))
                if ob is not None:
                    # If the portal root has an object by this name,
                    # don't allow an override.
                    # FIXME: needed to allow index_html for join code
                    if hasattr(ob, id) and id != 'index_html':
                        raise 'Bad Request', (
                            'The id "%s" is reserved.' % id)
                    # Otherwise we're ok.

    def _verifyObjectPaste(self, object, validate_src=1):
        # This assists the version in OFS.CopySupport.
        # It enables the clipboard to function correctly
        # with objects created by a multi-factory.
        if (hasattr(object, '__factory_meta_type__') and
            hasattr(self, 'all_meta_types')):
            mt = object.__factory_meta_type__
            method_name=None
            permission_name = None
            meta_types = self.all_meta_types
            if callable(meta_types): meta_types = meta_types()
            for d in meta_types:
                if d['name']==mt:
                    method_name=d['action']
                    permission_name = d.get('permission', None)
                    break

            if permission_name is not None:
                if getSecurityManager().checkPermission(permission_name,self):
                    if not validate_src:
                        # We don't want to check the object on the clipboard
                        return
                    try: parent = aq_parent(aq_inner(object))
                    except: parent = None
                    if getSecurityManager().validate(None, parent,
                                                     None, object):
                        # validation succeeded
                        return
                    raise 'Unauthorized', absattr(object.id)
                else:
                    raise 'Unauthorized', permission_name
            #
            # Old validation for objects that may not have registered 
            # themselves in the proper fashion.
            #
            elif method_name is not None:
                meth=self.unrestrictedTraverse(method_name)
                if hasattr(meth, 'im_self'):
                    parent = meth.im_self
                else:
                    try:    parent = aq_parent(aq_inner(meth))
                    except: parent = None
                if getSecurityManager().validate(None, parent, None, meth):
                    # Ensure the user is allowed to access the object on the
                    # clipboard.
                    if not validate_src:
                        return
                    try: parent = aq_parent(aq_inner(object))
                    except: parent = None
                    if getSecurityManager().validate(None, parent,
                                                     None, object):
                        return
                    id = object.id
                    if callable(id): id = id()
                    raise 'Unauthorized', id
                else:
                    raise 'Unauthorized', method_name
        PortalFolder.inheritedAttribute(
            '_verifyObjectPaste')(self, object, validate_src)

    security.setPermissionDefault(AddPortalContent, ('Owner','Manager'))
    security.setPermissionDefault(AddPortalFolders, ('Owner','Manager'))
    


class ContentFilter:
    """
        Represent a predicate against a content object's metadata.
    """
    MARKER = []
    filterSubject = filterType = []
    def __init__( self
                , Title=MARKER
                , Creator=MARKER
                , Subject=MARKER
                , Description=MARKER
                , created=MARKER
                , created_usage='range:min'
                , modified=MARKER
                , modified_usage='range:min'
                , Type=MARKER
                , **Ignored
                ):

        self.predicates = []

        if Title is not self.MARKER: 
            self.filterTitle = Title
            self.predicates.append( lambda x, pat=re( Title ):
                                      pat.search( x.Title() ) )

        if Creator is not self.MARKER: 
            self.predicates.append( lambda x, pat=re( Creator ):
                                      pat.search( x.Creator() ) )

        if Subject and Subject is not self.MARKER: 
            self.filterSubject = Subject
            self.predicates.append( self.hasSubject )

        if Description is not self.MARKER: 
            self.predicates.append( lambda x, pat=re( Description ):
                                      pat.search( x.Description() ) )

        if created is not self.MARKER: 
            if created_usage == 'range:min':
                self.predicates.append( lambda x, cd=created:
                                          cd <= x.created() )
            if created_usage == 'range:max':
                self.predicates.append( lambda x, cd=created:
                                          cd >= x.created() )

        if modified is not self.MARKER: 
            if modified_usage == 'range:min':
                self.predicates.append( lambda x, md=modified:
                                          md <= x.modified() )
            if modified_usage == 'range:max':
                self.predicates.append( lambda x, md=modified:
                                          md >= x.modified() )

        if Type:
            if type( Type ) == type( '' ):
                Type = [ Type ]
            self.filterType = Type
            self.predicates.append( lambda x, Type=Type:
                                      x.Type() in Type )

    def hasSubject( self, obj ):
        """
        Converts Subject string into a List for content filter view.
        """
        for sub in obj.Subject():
            if sub in self.Subject:
                return 1
        return 0

    def __call__( self, content ):

        for predicate in self.predicates:

            try:
                if not predicate( content ):
                    return 0
            except:
                return 0
        
        return 1

    def __str__( self ):
        """
        """
        return "Subject: %s; Type: %s" % ( self.filterSubject, self.filterType )

def absattr(attr):
    if callable(attr): return attr()
    else: return attr

manage_addPortalFolder = PortalFolder.manage_addPortalFolder
manage_addPortalFolderForm = HTMLFile( 'folderAdd', globals() )

Globals.InitializeClass(PortalFolder)
