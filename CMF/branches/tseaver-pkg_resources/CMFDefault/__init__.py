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
""" Default implementation of CMFCore.

$Id$
"""


cmfdefault_globals = globals()

def initialize( context ):

    from Products.CMFCore.DirectoryView import registerDirectory
    from Products.CMFCore.utils import ToolInit
    from Products.CMFCore.utils import ContentInit
    from Products.CMFCore.utils import registerIcon
    from Products.GenericSetup import BASE
    from Products.GenericSetup import EXTENSION
    from Products.GenericSetup import profile_registry

    import DefaultWorkflow
    import DiscussionItem
    import DiscussionTool
    import Document
    import DublinCore
    import Favorite
    import File
    import Image
    import Link
    import MembershipTool
    import MetadataTool
    import NewsItem
    import Portal
    import PropertiesTool
    import RegistrationTool
    import SkinnedFolder
    import SyndicationTool
    import factory
    import utils
    from permissions import AddPortalContent

    tools = ( DiscussionTool.DiscussionTool
            , MembershipTool.MembershipTool
            , RegistrationTool.RegistrationTool
            , PropertiesTool.PropertiesTool
            , MetadataTool.MetadataTool
            , SyndicationTool.SyndicationTool
            )

    ToolInit( 'CMF Default Tool'
            , tools=tools
            , icon='tool.gif'
            ).initialize( context )

    contentClasses = ( Document.Document
                    , File.File
                    , Image.Image
                    , Link.Link
                    , Favorite.Favorite
                    , NewsItem.NewsItem
                    , SkinnedFolder.SkinnedFolder
                    )

    contentConstructors = ( Document.addDocument
                        , File.addFile
                        , Image.addImage
                        , Link.addLink
                        , Favorite.addFavorite
                        , NewsItem.addNewsItem
                        , SkinnedFolder.addSkinnedFolder
                        )

    ContentInit( 'CMF Default Content'
               , content_types=contentClasses
               , permission=AddPortalContent
               , extra_constructors=contentConstructors
               ).initialize( context )

    profile_registry.registerProfile('default',
                                     'CMFDefault Site',
                                     'Profile for a default CMFSite.',
                                     'profiles/default',
                                     'CMFDefault',
                                     BASE)

    profile_registry.registerProfile('sample_content',
                                     'Sample CMFDefault Content',
                                     'Content for a sample CMFSite.',
                                     'profiles/sample_content',
                                     'CMFDefault',
                                     EXTENSION)

    context.registerClass( Portal.CMFSite
                         , constructors=(factory.addConfiguredSiteForm,
                                         factory.addConfiguredSite)
                         , icon='images/portal.gif'
                         )

    registerDirectory('skins', cmfdefault_globals)
    registerDirectory('help', cmfdefault_globals)

    registerIcon( DefaultWorkflow.DefaultWorkflowDefinition
                , 'images/workflow.gif'
                , cmfdefault_globals
                )

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

        context.registerHelpTitle('CMF Default Help')
