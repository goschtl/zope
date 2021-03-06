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
 
import Globals
from Products.CMFCore.PortalObject import PortalObjectBase
from Products.CMFCore import PortalFolder
from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.utils import getToolByName
from Products.CMFTopic import Topic, topic_globals
from DublinCore import DefaultDublinCoreImpl

import Document, Image, File, Link, NewsItem, Favorite
import DiscussionItem, SkinnedFolder

factory_type_information = ( Document.factory_type_information
                           + Image.factory_type_information
                           + File.factory_type_information
                           + Link.factory_type_information
                           + NewsItem.factory_type_information
                           + Favorite.factory_type_information
                           + DiscussionItem.factory_type_information
                           + SkinnedFolder.factory_type_information
                           )


class CMFSite ( PortalObjectBase
              , DefaultDublinCoreImpl
              ):
    """
        The *only* function this class should have is to help in the setup
        of a new CMFSite.  It should not assist in the functionality at all.
    """
    meta_type = 'CMF Site'

    _properties = (
        {'id':'title', 'type':'string'},
        {'id':'description', 'type':'text'},
        )
    title = ''
    description = ''

    __ac_permissions__=( ( 'Manage portal', ('manage_migrate_content',) )
                       , ( 'Add portal content', () )
                       , ( 'Add portal folders', () )
                       , ( 'List portal members', () )
                       , ( 'Reply to item', () )
                       , ( 'View',  ( 'isEffective', ) )
                       )

    def __init__( self, id, title='' ):
        PortalObjectBase.__init__( self, id, title )
        DefaultDublinCoreImpl.__init__( self )

    def isEffective( self, date ):
        """
            Override DefaultDublinCoreImpl's test, since we are always viewable.
        """
        return 1

    def reindexObject( self ):
        """
            Override DefaultDublinCoreImpl's method (so that we can play
            in 'editMetadata').
        """
        pass

    #
    #   The following two methods allow conversion of portal content from
    #   PTK version 0.7.1.
    #   DO NOT REMOVE!!!
    #
    if 0:
        def manage_migrate_content(self, REQUEST):
            """
                Converts instances of Products.PTKBase.<content> to
                instances of Products.PTKDemo.<content>.
            """
            import Products.PTKBase.Document
            import Products.PTKBase.File
            import Products.PTKBase.Image
            import Products.PTKBase.Link
            import Products.PTKBase.NewsItem
            import NewsItem, Link, Document, File, Image

            migrations = {
                Products.PTKBase.Document.Document : Document.Document,
                Products.PTKBase.File.File         : File.File,
                Products.PTKBase.Image.Image       : Image.Image,
                Products.PTKBase.Link.Link         : Link.Link,
                Products.PTKBase.NewsItem.NewsItem : NewsItem.NewsItem,
                }

            visited = []
            migrated = []
            self.__migrate_branches(migrations, self, migrated, visited)
            from string import join
            return 'Converted:\n%s\n\nDone.' % join(migrated, '\n')

        def __migrate_branches(self, migrations, branch, migrated, visited):
            base = getattr(branch, 'aq_base', branch)
            if base in visited:
                # Don't visit again!
                return
            visited.append(base)

            try: changed = branch._p_changed
            except: changed = 1
            for id in branch.objectIds():
                obj = branch._getOb(id)
                obase = getattr(obj, 'aq_base', obj)
                klass = obase.__class__
                if migrations.has_key(klass):
                    # Replace this object.
                    changed = 1
                    newob = migrations[klass](obase.id)
                    newob.id = obase.id   # This line activates obase.
                    newob.__dict__.update(obase.__dict__)
                    setattr(branch, id, newob)
                    migrated.append(obj.absolute_url())
                elif hasattr(obase, 'objectIds'):
                    # Enter a sub-branch.
                    self.__migrate_branches(migrations, obj, migrated, visited)
                else:
                    # Unload this object if it has not been changed.
                    try:
                        if obj._p_changed is None:
                            obj._p_deactivate()
                    except: pass
            if changed is None:
                # Unload this branch.
                object._p_deactivate()

        del visited[-1]

    else:   # placeholder
        def manage_migrate_content( self, REQUEST ):
            pass

Globals.default__class_init__(CMFSite)


class PortalGenerator:

    klass = CMFSite

    def setupTools(self, p):
        """Set up initial tools"""

        addCMFCoreTool = p.manage_addProduct['CMFCore'].manage_addTool
        addCMFCoreTool('CMF Actions Tool', None)
        addCMFCoreTool('CMF Catalog', None)
        addCMFCoreTool('CMF Member Data Tool', None)
        addCMFCoreTool('CMF Skins Tool', None)
        addCMFCoreTool('CMF Types Tool', None)
        addCMFCoreTool('CMF Undo Tool', None)
        addCMFCoreTool('CMF Workflow Tool', None)

        addCMFDefaultTool = p.manage_addProduct['CMFDefault'].manage_addTool
        addCMFDefaultTool('Default Discussion Tool', None)
        addCMFDefaultTool('Default Membership Tool', None)
        addCMFDefaultTool('Default Registration Tool', None)
        addCMFDefaultTool('Default URL Tool', None)
        addCMFDefaultTool('Default Properties Tool', None)
        addCMFDefaultTool('Default Metadata Tool', None)
        addCMFDefaultTool('Default Syndication Tool', None)

    def setupMailHost(self, p):
        p.manage_addProduct['MailHost'].manage_addMailHost(
            'MailHost', smtp_host='localhost')

    def setupUserFolder(self, p):
        p.manage_addProduct['OFSP'].manage_addUserFolder()

    def setupCookieAuth(self, p):
        p.manage_addProduct['CMFCore'].manage_addCC(
            id='cookie_authentication')

    def setupMembersFolder(self, p):
        PortalFolder.manage_addPortalFolder(p, 'Members')
        p.Members.manage_addProduct['OFSP'].manage_addDTMLMethod(
            'index_html', 'Member list', '<dtml-return roster>')

    def setupRoles(self, p):
        # Set up the suggested roles.
        p.__ac_roles__ = ('Member', 'Reviewer',)

    def setupPermissions(self, p):
        # Set up some suggested role to permission mappings.
        mp = p.manage_permission

        mp('Set own password',        ['Member','Manager',],    1)
        mp('Set own properties',      ['Member','Manager',],    1)
        mp('Add portal content',      ['Owner','Manager',],     1)
        mp('Add portal folders',      ['Owner','Manager',],     1)
        mp('Review portal content',   ['Reviewer','Manager',],  1)
        mp('Access future portal content',
                                      ['Reviewer','Manager',],  1)
        mp('List portal members',     ['Member','Manager',],    1)
        mp('Reply to item',           ['Member','Manager',],    1)

        # Add some other permissions mappings that may be helpful.
        mp('Delete objects',          ['Owner','Manager',],     1)
        mp('FTP access',              ['Owner','Manager',],     1)
        mp('Manage properties',       ['Owner','Manager',],     1)
        mp('Undo changes',            ['Owner','Manager',],     1)
        mp('View management screens', ['Owner','Manager',],     1)

    def setupDefaultSkins(self, p):
        from Products.CMFCore.DirectoryView import addDirectoryViews
        ps = getToolByName(p, 'portal_skins')
        addDirectoryViews(ps, 'skins', globals())
        addDirectoryViews(ps, 'skins', topic_globals)
        ps.manage_addProduct['OFSP'].manage_addFolder(id='custom')
        ps.addSkinSelection('Basic',
            'custom, topic, content, generic, control, Images',
            make_default=1)
        ps.addSkinSelection('Nouvelle',
            'nouvelle, custom, topic, content, generic, control, Images')
        ps.addSkinSelection('No CSS',
            'no_css, custom, topic, content, generic, control, Images')
        p.setupCurrentSkin()

    def setupTypes(self, p, initial_types=factory_type_information):
        tool = getToolByName(p, 'portal_types', None)
        if tool is None:
            return
        for t in initial_types:
            cfm = apply(ContentFactoryMetadata, (), t)
            tool._setObject(t['id'], cfm)
        
    def setupMimetypes(self, p):
        p.manage_addProduct[ 'CMFCore' ].manage_addRegistry()
        reg = p.content_type_registry

        reg.addPredicate( 'link', 'extension' )
        reg.getPredicate( 'link' ).edit( extensions="url, link" )
        reg.assignTypeName( 'link', 'Link' )

        reg.addPredicate( 'news', 'extension' )
        reg.getPredicate( 'news' ).edit( extensions="news" )
        reg.assignTypeName( 'news', 'News Item' )

        reg.addPredicate( 'document', 'major_minor' )
        reg.getPredicate( 'document' ).edit( major="text", minor="" )
        reg.assignTypeName( 'document', 'Document' )

        reg.addPredicate( 'image', 'major_minor' )
        reg.getPredicate( 'image' ).edit( major="image", minor="" )
        reg.assignTypeName( 'image', 'Image' )

        reg.addPredicate( 'file', 'major_minor' )
        reg.getPredicate( 'file' ).edit( major="application", minor="" )
        reg.assignTypeName( 'file', 'File' )


    def setupWorkflow(self, p):
        tool = getToolByName(p, 'portal_workflow', None)
        if tool is None:
            return
        from DefaultWorkflow import DefaultWorkflowDefinition
        id = 'default_workflow'
        tool._setObject(id, DefaultWorkflowDefinition(id))

    def setup(self, p, create_userfolder):
        self.setupTools(p)
        self.setupMailHost(p)
        if int(create_userfolder) != 0:
            self.setupUserFolder(p)
        self.setupCookieAuth(p)
        self.setupMembersFolder(p)
        self.setupRoles(p)
        self.setupPermissions(p)
        self.setupDefaultSkins(p)

        #   SkinnedFolders are only for customization;
        #   they aren't a default type.
        default_types = tuple( filter( lambda x: x['id'] != 'Skinned Folder'
                                     , factory_type_information ) )
        self.setupTypes(p, default_types )

        self.setupTypes(p, PortalFolder.factory_type_information)
        self.setupTypes(p, Topic.factory_type_information)
        self.setupMimetypes(p)
        self.setupWorkflow(p)

    def create(self, parent, id, create_userfolder):
        id = str(id)
        portal = self.klass(id=id)
        parent._setObject(id, portal)
        # Return the fully wrapped object.
        p = parent.this()._getOb(id)
        self.setup(p, create_userfolder)
        return p

    def setupDefaultProperties(self, p, title, description,
                               email_from_address, email_from_name,
                               validate_email,
                               ):
        p._setProperty('email_from_address', email_from_address, 'string')
        p._setProperty('email_from_name', email_from_name, 'string')
        p._setProperty('validate_email', validate_email and 1 or 0, 'boolean')
        p.title = title
        p.description = description


manage_addCMFSiteForm = Globals.HTMLFile('dtml/addPortal', globals())
manage_addCMFSiteForm.__name__ = 'addPortal'

def manage_addCMFSite(self, id, title='Portal', description='',
                         create_userfolder=1,
                         email_from_address='postmaster@localhost',
                         email_from_name='Portal Administrator',
                         validate_email=0, RESPONSE=None):
    '''
    Adds a portal instance.
    '''
    gen = PortalGenerator()
    p = gen.create(self, id, create_userfolder)
    gen.setupDefaultProperties(p, title, description,
                               email_from_address, email_from_name,
                               validate_email)
    if RESPONSE is not None:
        RESPONSE.redirect(p.absolute_url() + '/finish_portal_construction')
