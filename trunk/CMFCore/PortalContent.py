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
import string, urllib

import Globals
from DateTime import DateTime
from Globals import HTMLFile
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from CMFCorePermissions import AccessContentsInformation, View, \
     ReviewPortalContent, ModifyPortalContent
import CMFCorePermissions
from DynamicType import DynamicType

from ComputedAttribute import ComputedAttribute
from Acquisition import aq_base


class PortalContent(SimpleItem, DynamicType):
    """
        Base class for portal objects.
        
        Provides hooks for reviewing, indexing, and CMF UI.

        Derived classes must implement the interface described in
        interfaces/DublinCore.py.
    """

    isPortalContent = 1

    review_history=()
    review_state='private'  # or 'pending' or 'published'
    
    manage_options=(
        {'label':'View', 'action':'view'},
        {'label':'Security', 'action':'manage_access'},
        )
    

    security = ClassSecurityInfo()

    # indexed methods
    # ---------------
    
    security.declareProtected(View, 'SearchableText')
    def SearchableText(self):
        "Returns a concatination of all searchable text"
        # Should be overriden by portal objects
        return "%s %s" % (self.Title(), self.Description())

    # Support for dynamic icons

    security.declareProtected(AccessContentsInformation, 'getIcon')
    def getIcon(self):
        """
        getIcon is the preferred method to retrieve an icon for a 
        content item. using this method allows the content class
        creator to grab icons on the fly instead of using a fixed
        attribute on the class. used for the Favorites content class.
        """
        return getattr(self, 'icon', '/misc_/OFSP/dtmldoc.gif')

            
    # Reviewing methods
    # -----------------
    
    # Attributes:
    #   'review_state'   indicates state of object,
    #                    'published'|'private'|'pending'
    #   'review_history' is a list of dicts which describes a
    #                    history of reviewing actions
    #                    
    # Permissions:
    #
    # 'Review portal content'   permission to review an object for publishing
    # 'Request review'          permission to request an object be published
    
    security.declarePrivate('getReviewState')
    def getReviewState(self):
        return self.review_state

    security.declarePrivate('setReviewState')
    def setReviewState(self, review_state, comment):
        self.review_state = review_state

        rh = self.review_history
        rh = rh + ({
            'actor': self.portal_membership.getAuthenticatedMember() \
            .getUserName(),
            'action': 'Made ' + review_state,
            'review_state': review_state,
            'time': DateTime(),
            'comments': comment,
            },)
        self.review_history = rh

    # Cataloging methods
    # ------------------

    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self):
        catalog = getattr(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.indexObject(self)

    security.declareProtected(ModifyPortalContent, 'unindexObject')
    def unindexObject(self):
        catalog = getattr(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.unindexObject(self)

    security.declarePrivate('reindexObject')
    def reindexObject(self):
        catalog = getattr(self, 'portal_catalog', None)
        if catalog is not None:
            catalog.reindexObject(self)
        
    def manage_afterAdd(self, item, container):
        "Add self to the catalog."
        if aq_base(item) is aq_base(self):
            self.indexObject()

    def manage_beforeDelete(self, item, container):
        "Remove self from the catalog."
        if aq_base(item) is aq_base(self):
            self.unindexObject()

    # Contentish interface methods
    # ----------------------------

    security.declarePrivate('listActions')
    def listActions(self, info):
        # Report toolbox actions applicable to all kinds of content
        content_url = info.content_url
        return (
            {'name':'Status history',
             'url': content_url + '/content_status_history',
             'permissions': ['Request review', 'Review portal content'],
             'category': 'object'
             },
            )

    def _index_html(self):
        '''
        Invokes the first customizable action.
        '''
        ti = self.getTypeInfo()
        actions = ti.getActions()
        if actions:
            path = actions[0]['action']
            return self.restrictedTraverse(path)
        raise 'Not Found', ('No default view defined for %s' %
                            self.getPhysicalPath())

    security.declareProtected(CMFCorePermissions.View, 'index_html')
    index_html = ComputedAttribute(_index_html, 1)

    security.declareProtected(CMFCorePermissions.View, 'view')
    view = index_html  # Necessary for catalog searches.


Globals.InitializeClass(PortalContent)
