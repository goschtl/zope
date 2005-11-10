##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Portal services base objects

$Id$
"""

cmfcore_globals = globals()

# Because persistent objects may be out there which were
# created when the module was in that product, we need
# __module_aliases__ . 
import CMFBTreeFolder
__module_aliases__ = ( ( 'Products.BTreeFolder2.CMFBTreeFolder'
                       , 'Products.CMFCore.CMFBTreeFolder'
                       )
                     ,
                     )

def initialize(context):

    import ActionInformation
    import ActionsTool
    import CachingPolicyManager
    import CatalogTool
    import ContentTypeRegistry
    import CookieCrumbler
    import DirectoryView
    import DiscussionTool
    import fiveactionstool
    import FSDTMLMethod
    import FSFile
    import FSImage
    import FSPageTemplate
    import FSPropertiesObject
    import FSPythonScript
    import FSSTXMethod
    import FSZSQLMethod
    import MemberDataTool
    import MembershipTool
    import PortalContent
    import PortalFolder
    import PortalObject
    import RegistrationTool
    import SkinsTool
    import TypesTool
    import UndoTool
    import URLTool
    import utils
    import WorkflowTool

    from interfaces import IAction
    from interfaces import IActionCategory
    from interfaces import ITypeInformation
    from permissions import AddPortalFolders
    from permissions import ManagePortal


    tools = (
        MembershipTool.MembershipTool,
        RegistrationTool.RegistrationTool,
        WorkflowTool.WorkflowTool,
        CatalogTool.CatalogTool,
        DiscussionTool.DiscussionTool,
        ActionsTool.ActionsTool,
        UndoTool.UndoTool,
        SkinsTool.SkinsTool,
        MemberDataTool.MemberDataTool,
        TypesTool.TypesTool,
        URLTool.URLTool,
        fiveactionstool.FiveActionsTool,
        )

    FolderConstructorForm = ( 'manage_addPortalFolderForm'
                            , PortalFolder.manage_addPortalFolderForm
                            )

    _CONTENT_TYPES = ( PortalFolder.PortalFolder
                    ,  CMFBTreeFolder.CMFBTreeFolder
                    )

    _EXTRA_CONSTRUCTORS = ( PortalFolder.manage_addPortalFolder
                        ,  CMFBTreeFolder.manage_addCMFBTreeFolder
                        )

    context.registerClass(
        DirectoryView.DirectoryViewSurrogate,
        constructors=(('manage_addDirectoryViewForm',
                       DirectoryView.manage_addDirectoryViewForm),
                      DirectoryView.manage_addDirectoryView,
                      DirectoryView.manage_listAvailableDirectories,
                      ),
        icon='images/dirview.gif'
        )

    context.registerClass(
        CookieCrumbler.CookieCrumbler,
        constructors=(CookieCrumbler.manage_addCCForm,
                      CookieCrumbler.manage_addCC),
        icon = 'images/cookie.gif'
        )

    context.registerClass(
        ContentTypeRegistry.ContentTypeRegistry,
        constructors=( ContentTypeRegistry.manage_addRegistry, ),
        icon = 'images/registry.gif'
        )

    context.registerClass(
        CachingPolicyManager.CachingPolicyManager,
        constructors=( CachingPolicyManager.manage_addCachingPolicyManager, ),
        icon = 'images/registry.gif'
        )

    context.registerClass(
        ActionInformation.ActionCategory,
        permission=ManagePortal,
        constructors=(ActionInformation.manage_addActionCategoryForm,
                      ActionInformation.manage_addActionCategory),
        icon='images/cmf_action_category.gif',
        visibility=None,
        interfaces=(IActionCategory,))

    context.registerClass(
        ActionInformation.Action,
        permission=ManagePortal,
        constructors=(ActionInformation.manage_addActionForm,
                      ActionInformation.manage_addAction),
        icon='images/cmf_action.gif',
        visibility=None,
        interfaces=(IAction,))

    context.registerClass(
        TypesTool.FactoryTypeInformation,
        permission=ManagePortal,
        constructors=(TypesTool.manage_addFactoryTIForm,
                      TypesTool.manage_addTypeInfo),
        icon='images/typeinfo.gif',
        visibility=None,
        interfaces=(ITypeInformation,))

    context.registerClass(
        TypesTool.ScriptableTypeInformation,
        permission=ManagePortal,
        constructors=(TypesTool.manage_addScriptableTIForm,
                      TypesTool.manage_addTypeInfo),
        icon='images/typeinfo.gif',
        visibility=None,
        interfaces=(ITypeInformation,))

    utils.registerIcon(FSDTMLMethod.FSDTMLMethod,
                       'images/fsdtml.gif', cmfcore_globals)
    utils.registerIcon(FSPythonScript.FSPythonScript,
                       'images/fspy.gif', cmfcore_globals)
    utils.registerIcon(FSImage.FSImage,
                       'images/fsimage.gif', cmfcore_globals)
    utils.registerIcon(FSFile.FSFile,
                       'images/fsfile.gif', cmfcore_globals)
    utils.registerIcon(FSPageTemplate.FSPageTemplate,
                       'images/fspt.gif', cmfcore_globals)
    utils.registerIcon(FSPropertiesObject.FSPropertiesObject,
                       'images/fsprops.gif', cmfcore_globals)
    utils.registerIcon(FSZSQLMethod.FSZSQLMethod,
                       'images/fssqlmethod.gif', cmfcore_globals)

    utils.ToolInit( 'CMF Core Tool'
                  , tools=tools
                  , icon='tool.gif'
                  ).initialize( context )

    utils.ContentInit( 'CMF Core Content'
                     , content_types=_CONTENT_TYPES
                     , permission=AddPortalFolders
                     , extra_constructors=_EXTRA_CONSTRUCTORS
                     ).initialize( context )

    if 0:   # XXX: comment this out for now
        # make registerHelp work with 2 directories
        help = context.getProductHelp()
        lastRegistered = help.lastRegistered
        context.registerHelp(directory='help', clear=1)
        context.registerHelp(directory='interfaces', clear=1)
        if help.lastRegistered != lastRegistered:
            help.lastRegistered = None
            context.registerHelp(directory='help', clear=1)
            help.lastRegistered = None
            context.registerHelp(directory='interfaces', clear=0)
        context.registerHelpTitle('CMF Core Help')
