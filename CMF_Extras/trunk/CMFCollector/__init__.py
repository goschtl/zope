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
import sys

this_module = sys.modules[ __name__ ]
collector_globals = globals()

def initialize(context):
    from Products.CMFCore.interfaces import ISiteRoot
    from Products.CMFCore.DirectoryView import registerDirectory
    from Products.GenericSetup import EXTENSION
    from Products.GenericSetup import profile_registry

    import Collector
    import CollectorIssue
    import WebTextDocument
    import CollectorSubset
    from permissions import View
    from permissions import AddPortalContent
    from permissions import AddCollectorIssue
    from permissions import EditCollectorIssue
    from permissions import AddCollectorIssueFollowup

    factory_type_information = (
        (Collector.factory_type_information
        + CollectorIssue.factory_type_information
        + Collector.catalog_factory_type_information
        + CollectorSubset.factory_type_information

        + ({'id': 'Collector Issue Transcript',
            #     'content_icon': 'event_icon.gif',
            'meta_type': 'WebText Document',
            'description': (
                'A transcript of issue activity, including comments,'
                ' state changes, and so forth.'), 
            'product': 'CMFCollector',
            'factory': None,               # So not included in 'New' add form
            'allowed_content_types': None,
            'immediate_view': 'collector_transcript_view',
            'actions': (
                { 'id': 'view',
                    'name': 'View',
                    'action': 'string:${object_url}/../',
                    'permissions': (View,) },
                { 'id': 'addcomment',
                    'name': 'Add Comment',
                    'action':
                      'string:${object_url}/collector_transcript_comment_form',
                    'permissions':
                            (AddCollectorIssueFollowup,) },
                { 'id': 'edittranscript',
                    'name': 'Edit Transcript',
                    'action':
                         'string:${object_url}/collector_transcript_edit_form',
                    'permissions': (EditCollectorIssue,) },
                ),
            },
            )
        )
        )

    contentClasses = (Collector.Collector, CollectorIssue.CollectorIssue,
                    Collector.CollectorCatalog, CollectorSubset.CollectorSubset)
    contentConstructors = (Collector.addCollector,
                        CollectorIssue.addCollectorIssue,
                        CollectorSubset.addCollectorSubset)

    context.registerHelp(directory='help')
    context.registerHelpTitle('CMF Collector Help')

    context.registerClass(Collector.Collector,
                          constructors = (Collector.addCollector,),
                          permission = AddPortalContent)

    context.registerClass(CollectorIssue.CollectorIssue,
                          constructors = (CollectorIssue.addCollectorIssue,),
                          permission = AddCollectorIssue)

    context.registerClass(CollectorSubset.CollectorSubset,
                          constructors = (CollectorSubset.addCollectorSubset,),
                          permission = AddPortalContent)

    registerDirectory('skins', globals())
    registerDirectory('skins/collector', globals())

    profile_registry.registerProfile('CMFCollector',
                                     'CMF Collector',
                                     'Types, skins, workflow for collector.',
                                     'profiles/collector',
                                     'CMFCollector',
                                     EXTENSION,
                                     for_=ISiteRoot)
