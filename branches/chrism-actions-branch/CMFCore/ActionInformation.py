##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
""" Information about customizable actions.

$Id$
"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Globals import DTMLFile
from Acquisition import aq_inner, aq_parent
from OFS.SimpleItem import SimpleItem

from Expression import Expression
from CMFCorePermissions import View
from CMFCorePermissions import ManagePortal
from utils import _dtmldir
from utils import getToolByName
from types import StringType

class ActionInformation( SimpleItem ):

    """ Represent a single selectable action.
    
    Actions generate links to views of content, or to specific methods
    of the site.  They can be filtered via their conditions.
    """
    _isActionInformation = 1
    __allow_access_to_unprotected_subobjects__ = 1

    security = ClassSecurityInfo()
    _action_info = None

    def __init__( self, **kw):
        """ """
        if not kw.has_key('id'):
            raise ValueError, 'argument must include id'
        self.updateActionInfoDict(kw)

    security.declareProtected( View, 'Title' )
    def Title(self):

        """ Return the Action title.
        """
        return self._action_info['title'] or self.getId()

    security.declareProtected( View, 'Description' )
    def Description( self ):

        """ Return a description of the action.
        """
        return self._action_info['description']

    security.declarePrivate( 'testCondition' )
    def testCondition( self, ec ):

        """ Evaluate condition using context, 'ec', and return 0 or 1.
        """
        cond = self._action_info['condition']
        if cond:
            return cond(ec)
        else:
            return 1

    security.declarePublic( 'getAction' )
    def getAction( self, ec ):

        """ Compute the action using context, 'ec'; return a mapping of
            info about the action.
        """
        info = {}
        info.update(self._action_info)
        info['id'] = self.id
        info['name'] = self.Title()
        action_obj = self._getActionObject()
        info['url'] = action_obj and action_obj( ec ) or ''
        info['permissions'] = self.getPermissions()
        info['category'] = self.getCategory()
        info['visible'] = self.getVisibility()
        return info

    security.declarePrivate( '_getActionObject' )
    def _getActionObject( self ):

        """ Find the action object, working around name changes.
        """
        return self._action_info.get('action', None )

    security.declarePublic( 'getActionExpression' )
    def getActionExpression( self ):

        """ Return the text of the TALES expression for our URL.
        """
        action = self._getActionObject()
        return action and action.text or ''

    security.declarePublic( 'getCondition' )
    def getCondition(self):

        """ Return the text of the TALES expression for our condition.
        """
        cond = self._action_info['condition']
        if hasattr(cond, 'text'):
            return cond.text
        return ''

    security.declarePublic( 'getPermission' )
    def getPermissions( self ):

        """ Return the permission, if any, required to execute the action.

        Return an empty tuple if no permission is required.
        """
        return self._action_info['permissions']

    security.declarePublic( 'getCategory' )
    def getCategory( self ):

        """ Return the category in which the action should be grouped.
        """
        return self._action_info.get('category') or 'object'

    security.declarePublic( 'getVisibility' )
    def getVisibility( self ):

        """ Return whether the action should be visible in the CMF UI.
        """
        return self._action_info['visible']

    security.declarePrivate( 'clone' )
    def clone( self ):

        """ Return a newly-created AI just like us.
        """
        kw = self._action_info.copy()
        return apply(self.__class__, (), kw)

    security.declarePrivate('getActionInfo')
    def getActionInfoDict( self ):
        return self._action_info.copy()

    security.declarePrivate('updateActionInfo')
    def updateActionInfoDict( self, kw ):
        if self._action_info is None:
            self._action_info = {}
        kw['id'] = kw.get('id', getattr(self, 'id'))
        kw['title'] = kw.get('title', '')
        kw['description'] = kw.get('description', '')
        kw['category'] = kw.get('category', 'object')
        kw['condition'] = kw.get('condition', '')
        kw['permissions'] = kw.get('permissions', ())
        kw['priority'] = kw.get('priority', 10)
        kw['visible'] = kw.get('visible', 1)
        kw['action'] = kw.get('action', '')
        condition = kw['condition'] = kw.get('condition', '')
        if condition and isinstance(condition, StringType):
            condition = kw['condition'] = Expression( condition )

        action = kw['action'] = kw.get('action', '')
        if action and isinstance(action, StringType):
            action = kw['action'] = Expression( action )
        self._action_info.update(kw)
        self.id = kw['id']

    security.declarePublic('query')
    def query(self, name, default=None):
        """ returns the item named by name in _action_info_dict or default """
        return self._action_info.get(name, default)

    def __setstate__(self, state):
        if not state.has_key('_action_info'):
            kw = {}
            for name in ('id', 'title', 'description', 'category', 'condition',
                         'permissions', 'priority', 'visible', 'action'):
                kw[name] = state.get(name)
                del state[name]
            self._action_info = kw
            self.__dict__.update(state)

InitializeClass( ActionInformation )

class oai:
    #Provided for backwards compatability
    # Provides information that may be needed when constructing the list of
    # available actions.
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__( self, tool, folder, object=None ):
        self.portal = portal = aq_parent(aq_inner(tool))
        membership = getToolByName(tool, 'portal_membership')
        self.isAnonymous = membership.isAnonymousUser()
        self.user_id = membership.getAuthenticatedMember().getUserName()
        self.portal_url = portal.absolute_url()
        if folder is not None:
            self.folder_url = folder.absolute_url()
            self.folder = folder
        else:
            self.folder_url = self.portal_url
            self.folder = portal
        self.content = object
        if object is not None:
            self.content_url = object.absolute_url()
        else:
            self.content_url = None

    def __getitem__(self, name):
        # Mapping interface for easy string formatting.
        if name[:1] == '_':
            raise KeyError, name
        if hasattr(self, name):
            return getattr(self, name)
        raise KeyError, name

