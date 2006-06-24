##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Bug Tracker System PlacelessSetup

Since it requires **a lot** of basic setup for the simplest integration unit
tests between Bug Tracker and Bu, a seperate setup mixin seems very
appropriate.

$Id: placelesssetup.py,v 1.3 2003/07/28 20:38:38 srichter Exp $
"""
from datetime import datetime

from zope.component.interfaces import IFactory
from zope.interface import classImplements, implements
from zope.schema.vocabulary import getVocabularyRegistry

from zope.app import zapi
from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import PlacelessSetup as SetupBase
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.file import File
from zope.app.container.interfaces import INameChooser
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.app.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.app.dublincore.interfaces import IWriteZopeDublinCore
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.location.interfaces import ILocation
from zope.app.location.traversing import LocationPhysicallyLocatable
from zope.app.renderer.plaintext import IPlainTextSource
from zope.app.renderer.plaintext import PlainTextToHTMLRenderer
from zope.app.renderer.plaintext import PlainTextSourceFactory
from zope.app.security.interfaces import IAuthentication
from zope.app.size.interfaces import ISized
from zope.app.traversing.interfaces import IContainmentRoot, ITraverser
from zope.app.traversing.interfaces import ITraversable, IPhysicallyLocatable
from zope.app.security.principalregistry import principalRegistry
from zope.app.size import DefaultSized
from zope.app.traversing.adapters import DefaultTraversable, Traverser
from zope.app.traversing.interfaces import IPhysicallyLocatable

from bugtracker.bug import Bug, BugDependencyAdapter
from bugtracker.comment import Comment
from bugtracker.interfaces import IBug, IBugTracker
from bugtracker.interfaces import IBugDependencies
from bugtracker.interfaces import IStatusVocabulary, IPriorityVocabulary
from bugtracker.interfaces import IBugTypeVocabulary, IReleaseVocabulary
from bugtracker.renderable import RenderableText
from bugtracker.tracker import BugTracker, BugTrackerNameChooser
from bugtracker.vocabulary import StatusVocabulary, PriorityVocabulary
from bugtracker.vocabulary import BugTypeVocabulary, ReleaseVocabulary
from bugtracker.vocabulary import UserVocabulary

class Root(object):
    implements(IContainmentRoot)
    __parent__ = None
    __name__ = ''

class PlacelessSetup(SetupBase):

    def setUp(self):
        SetupBase.setUp(self)
        classImplements(Bug, IAttributeAnnotatable)
        classImplements(BugTracker, IAttributeAnnotatable)
        classImplements(Comment, IAttributeAnnotatable)
        classImplements(File, IAttributeAnnotatable)
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                             AttributeAnnotations)
        ztapi.provideAdapter(IAttributeAnnotatable, IWriteZopeDublinCore,
                             ZDCAnnotatableAdapter)
        ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                             LocationPhysicallyLocatable)
        ztapi.provideAdapter(IBug, IBugDependencies, BugDependencyAdapter)
        ztapi.provideAdapter(None, ITraverser, Traverser)
        ztapi.provideAdapter(None, ITraversable, DefaultTraversable)
        ztapi.provideAdapter(None, ISized, DefaultSized)

        ztapi.provideUtility(IFactory, PlainTextSourceFactory,
                             u'zope.source.plaintext')
        ztapi.browserView(IPlainTextSource, '', PlainTextToHTMLRenderer)

        ztapi.provideAdapter(IBugTracker, IStatusVocabulary, StatusVocabulary)
        ztapi.provideAdapter(IBugTracker, IPriorityVocabulary,
                             PriorityVocabulary)
        ztapi.provideAdapter(IBugTracker, IReleaseVocabulary, ReleaseVocabulary)
        ztapi.provideAdapter(IBugTracker, IBugTypeVocabulary, BugTypeVocabulary)

        ztapi.provideAdapter(IBugTracker, INameChooser, BugTrackerNameChooser)

        registry = getVocabularyRegistry()
        registry.register('Stati', StatusVocabulary)
        registry.register('Priorities', PriorityVocabulary)
        registry.register('BugTypes', BugTypeVocabulary)
        registry.register('Releases', ReleaseVocabulary)
        registry.register('Users', UserVocabulary)

        ztapi.provideUtility(IAuthentication, principalRegistry)

        principalRegistry.definePrincipal(u'zope.srichter',
                                          u'Stephan Richter', u'',
                                          'srichter', 'foo')
        principalRegistry.definePrincipal(u'zope.jim',
                                          u'Jim Fulton', u'',
                                          'jim', 'bar')
        principalRegistry.definePrincipal(u'zope.stevea',
                                          u'Steve Alexander', u'',
                                          'stevea', 'blah')


    def generateTracker(self):
        tracker = BugTracker()
        tracker.__parent__ = Root()
        tracker.__name__ = "tracker"
        vocab = IStatusVocabulary(tracker)
        vocab.add('new', u'New', True)
        vocab.add('open', u'Open')
        vocab.add('assigned', u'Assigned')
        vocab.add('deferred', u'Deferred')
        vocab.add('closed', u'Closed')
        vocab = IBugTypeVocabulary(tracker)
        vocab.add('bug', u'Bug', True)
        vocab.add('feature', u'Feature')
        vocab.add('release', u'Release')
        vocab = IReleaseVocabulary(tracker)
        vocab.add('None', u'(not specified)', True)
        vocab.add('zope_x3', u'Zope X3')
        vocab = IPriorityVocabulary(tracker)
        vocab.add('low', u'Low')
        vocab.add('normal', u'Normal', True)
        vocab.add('urgent', u'Urgent')
        vocab.add('critical', u'Critical')
        return tracker

    def generateBug(self, id='1'):
        bug = Bug()
        bug.__parent__ = self.generateTracker()
        bug.__name__ = id
        bug.title = u'Bug %s' %id
        bug.description = RenderableText(u'This is Bug %s.' %id,
                                         'zope.source.plaintext')
        dc = IZopeDublinCore(bug)
        dc.created = datetime(2003, 03, 02+int(id), 03, 00, 00)
        dc.modified = datetime(2003, 03, 02+int(id), 04, 00, 00)
        dc.creators = [u'zope.srichter']
        bug.owners = [u'zope.jim', u'zope.stevea']
        comment = Comment()
        dc = IZopeDublinCore(comment)
        dc.creators = [u'zope.srichter']
        dc.created = datetime(2003, 03, 02+int(id), 05, 00, 00)
        comment.body = RenderableText('This is comment 1.',
                                      'zope.source.plaintext')
        bug['comment1'] = comment
        attach = File()
        dc = IZopeDublinCore(comment)
        dc.creators = [u'zope.srichter']
        dc.created = datetime(2003, 03, 02+int(id), 06, 00, 00)
        attach.data = 'This is an attachment.'
        bug['attach.txt'] = attach
        return bug
