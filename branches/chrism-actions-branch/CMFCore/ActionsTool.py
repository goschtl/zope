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

"""Basic action list tool.

$Id$
"""
__version__='$Revision$'[11:-2]


import OFS
from utils import UniqueObject, SimpleItemWithProperties, _getAuthenticatedUser, _checkPermission
from utils import getToolByName, _dtmldir, cookString
import CMFCorePermissions
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile, package_home
from urllib import quote
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from string import join
from Expression import Expression, createExprContext
from ActionInformation import ActionInformation, oai
from ActionProviderBase import ActionProviderBase
from TypesTool import TypeInformation
from types import DictionaryType

class ActionsTool(UniqueObject, OFS.Folder.Folder, ActionProviderBase):
    """
        Weave together the various sources of "actions" which are apropos
        to the current user and context.
    """
    id = 'portal_actions'
    _actions = [ActionInformation(id='folderContents'
                                , title='Folder contents'
                                , action=Expression(
               text='string: ${folder_url}/folder_contents')
                                , condition=Expression(
               text='python: folder is not object') 
                                , permissions=('List folder contents',)
                                , category='object'
                                , visible=1
                                 )
              , ActionInformation(id='folderContents'
                                , title='Folder contents'
                                , action=Expression(
               text='string: ${folder_url}/folder_contents')
                                , condition=Expression(
               text='python: folder is object')
                                , permissions=('List folder contents',)
                                , category='folder'
                                , visible=1
                                 )]

    meta_type = 'CMF Actions Tool'

    action_providers = ('portal_membership'
                      , 'portal_actions'
                      , 'portal_registration'
                      , 'portal_discussion'
                      , 'portal_undo'
                      , 'portal_syndication'
                      , 'portal_workflow'
                      , 'portal_properties')

    security = ClassSecurityInfo()

    manage_options = ( ActionProviderBase.manage_options +
                      ({'label' : 'Action Providers', 'action' : 'manage_actionProviders'}
                     ,   { 'label' : 'Overview', 'action' : 'manage_overview' }
                     ,
                     ) + OFS.Folder.Folder.manage_options
                     ) 

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainActionsTool', _dtmldir )
    manage_actionProviders = DTMLFile('manageActionProviders', _dtmldir)


    #
    # Programmatically manipulate the list of action providers
    #

    security.declarePrivate('listActions')
    def listActions(self, info=None):
        """
        Lists actions available through the tool.
        """
        return self._actions

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'listActionProviders'
                             )
    def listActionProviders(self):
       """ returns a sequence of action providers known by this tool """
       return self.action_providers

    security.declareProtected(CMFCorePermissions.ManagePortal
                            , 'manage_aproviders')
    def manage_aproviders(self
                        , apname=''
                        , chosen=()
                        , add_provider=0
                        , del_provider=0
                        , REQUEST=None):
        """
        Manage TTW Action Providers
        """
        providers = list(self.listActionProviders())
        new_providers = []
        if add_provider:
            providers.append(apname)
        elif del_provider:
            for item in providers:
                if item not in chosen:
                    new_providers.append(item)
            providers = new_providers
        self.action_providers = providers
        if REQUEST is not None:
            return self.manage_actionProviders(self
                                             , REQUEST
                                             , manage_tabs_message='Properties changed.')
        


    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'addActionProvider'
                             )
    def addActionProvider( self, provider_name ):
        """ add the name of a new action provider """
        if hasattr( self, provider_name ):
            p_old = self.action_providers
            p_new = p_old + ( provider_name, )
            self.action_providers = p_new

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'deleteActionProvider'
                             )
    def deleteActionProvider( self, provider_name ):
        """ remove an action provider """
        if provider_name in self.action_providers:
            p_old = list( self.action_providers )
            del p_old[p_old.index( provider_name)]
            self.action_providers = tuple( p_old )

    #
    #   'portal_actions' interface methods
    #

    security.declarePrivate('getProviderActions')
    def getProviderActions(self, info=None):
        # Return actions from specific tools.
        l = []
        for provider_name in self.listActionProviders():
            provider = getattr(self, provider_name)
            actions = provider.listActions(info)
            l.extend(actions)
        return l

    security.declarePrivate('getTypeActions')
    def getTypeActions(self, object, info=None):
        # Return actions from object.
        if object is None:
            return []
        
        l = []
        types_tool = getToolByName( self, 'portal_types' )
        # we might get None back from getTypeInfo.  We construct
        # a dummy TypeInformation object here in that case (the 'or'
        # case).  This prevents us from needing to check the condition.
        ti = types_tool.getTypeInfo( object ) or TypeInformation('Dummy')
        defs = ti.getActions()
        url = object_url = object.absolute_url()
        for d in defs:
            # we can't modify or expose the original actionsd... this
            # stems from the fact that getActions returns a ref to the
            # actual dictionary used to store actions instead of a
            # copy.  We copy it here to prevent it from being modified.
            d = d.copy()
            d['id'] = d.get('id', None)
            if d['action']:
                url = '%s/%s' % (object_url, d['action'])
            d['url'] = url
            d['category'] = d.get('category', 'object')
            d['visible'] = d.get('visible', 1)
            l.append(d)

        if hasattr(aq_base(object), 'listActions'):
            l.extend(object.listActions())

        return l

    def _findParentFolder(self, object):
        # Search up the object's containment hierarchy until we find an
        # object that claims it's a folder.
        context = object
        while not hasattr(aq_base(context), 'isPrincipiaFolderish'):
            new_context = aq_parent(aq_inner(context))
            if context is new_context:
                break
            context = new_context
        return context

    security.declarePublic('listFilteredActionsFor')
    def listFilteredActionsFor(self, object=None):
        '''Gets all actions available to the user and returns a mapping
        containing user actions, object actions, and global actions.
        '''
        actions = []
        portal = folder = aq_parent(aq_inner(self))

        if object is not None and hasattr(object, 'aq_base'):
            folder = self._findParentFolder(object)

        # include actions from types tool
        actions.extend(self.getTypeActions(object))

        # include actions from action providers
        actions.extend(self.getProviderActions(oai(self, folder, object)))

        # Reorganize the actions by category, filtering out disallowed actions.
        filtered_actions={
            'user':[], 'folder':[], 'object':[], 'global':[], 'workflow':[],
                          }
        expr_context = createExprContext(folder, portal, object)
        for action in actions:
            action, category = organizeAction(
                action, portal, folder, object, expr_context
                )
            if None in (action, category):
                continue
            catlist = filtered_actions.setdefault(category, [])
            if not action in catlist:
                # no dupes
                catlist.append(action)

        return filtered_actions

    # listFilteredActions is an alias for listFilteredActionsFor.
    security.declarePublic('listFilteredActions')
    listFilteredActions = listFilteredActionsFor

def organizeAction(action, portal, folder, object, expr_context):
    """ Organize the action into a category and expand the action
    into a dictionary if it is an ActionInformation object """
    if not isinstance(action, DictionaryType):
        # this is an ActionInformation object
        if not action.testCondition(expr_context):
            # it did not pass the condition
            return None, None
        action = action.getAction(expr_context)

    if action.get('visible', 1):
        category = action.get('category', 'object')
        permissions = action.get('permissions', None)
        # context will be one of object, folder, or portal
        if (object is not None and
            (category.startswith('object') or
             category.startswith('workflow'))):
            context = object
        elif (folder is not None and
              category.startswith('folder')):
            context = folder
        else:
            context = portal
        if permissions and not checkPermissions(permissions, context):
            # inadequate permissions to see the action
            return None, None

    return action, category

def checkPermissions(permissions, context):
    for permission in permissions:
        # The user must be able to match at least one of
        # the listed permissions.
        if _checkPermission(permission, context):
            return 1

InitializeClass(ActionsTool)
