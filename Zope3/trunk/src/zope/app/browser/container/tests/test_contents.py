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
"""

Revision information:
$Id: test_contents.py,v 1.11 2003/03/30 17:38:41 sidnei Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.adapter import provideAdapter

from zope.app.interfaces.traversing import ITraversable
from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.container import IContainer
from zope.app.interfaces.copypastemove import IObjectMover
from zope.app.container.zopecontainer import ZopeContainerAdapter

from zope.app.traversing import traverse
from zope.app.traversing import IObjectName
from zope.app.interfaces.copypastemove import IObjectMover
from zope.app.interfaces.copypastemove import IObjectCopier
from zope.app.interfaces.container import IPasteTarget
from zope.app.interfaces.container import IMoveSource
from zope.app.interfaces.container import ICopySource
from zope.app.interfaces.container import IPasteNamesChooser

from zope.app.traversing.adapters import ObjectName
from zope.app.copypastemove import ObjectMover
from zope.app.copypastemove import ObjectCopier
from zope.app.container.copypastemove import PasteTarget
from zope.app.container.copypastemove import MoveSource
from zope.app.container.copypastemove import CopySource
from zope.app.container.copypastemove import PasteNamesChooser
from zope.app.container.zopecontainer import ZopeContainerAdapter

from zope.app.event.tests.placelesssetup import getEvents
from zope.app.interfaces.event import IObjectRemovedEvent, IObjectModifiedEvent
from zope.interface import Interface
from zope.proxy.introspection import removeAllProxies

from zope.app.interfaces.copypastemove import IPrincipalClipboard
from zope.app.copypastemove import PrincipalClipboard
from zope.component import getAdapter, getService, getServiceManager
from zope.app.services.principalannotation \
    import PrincipalAnnotationService
from zope.app.interfaces.services.principalannotation \
    import IPrincipalAnnotationService
from zope.app.interfaces.annotation import IAnnotations

class BaseTestContentsBrowserView(PlacelessSetup):
    """Base class for testing browser contents.

    Subclasses need to define a method, '_TestView__newContext', that
    takes no arguments and that returns a new empty test view context.

    Subclasses need to define a method, '_TestView__newView', that
    takes a context object and that returns a new test view.
    """

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(IContainer, IZopeContainer, ZopeContainerAdapter)
        provideAdapter(ITraversable, IZopeContainer, ZopeContainerAdapter)
        provideAdapter(None, IObjectMover, ObjectMover)

    def testInfo(self):
        # Do we get the correct information back from ContainerContents?
        container = self._TestView__newContext()
        subcontainer = self._TestView__newContext()
        container.setObject('subcontainer', subcontainer)
        document = Document()
        container.setObject('document', document)

        fc = self._TestView__newView(container)
        info_list = fc.listContentInfo()

        self.assertEquals(len(info_list), 2)

        ids = map(lambda x: x['id'], info_list)
        self.assert_('subcontainer' in ids)

        objects = map(lambda x: x['object'], info_list)
        self.assert_(subcontainer in objects)

        urls = map(lambda x: x['url'], info_list)
        self.assert_('subcontainer' in urls)

        self.failIf(filter(None, map(lambda x: x['icon'], info_list)))

    def testInfoWDublinCore(self):
        container = self._TestView__newContext()
        document = Document()
        container.setObject('document', document)

        from datetime import datetime
        from zope.app.interfaces.dublincore import IZopeDublinCore
        from zope.app.browser.container.contents import formatTime
        class FauxDCAdapter:
            __implements__ = IZopeDublinCore

            def __init__(self, context):
                pass
            title = 'faux title'
            size = 1024
            created = datetime(2001, 1, 1, 1, 1, 1)
            modified = datetime(2002, 2, 2, 2, 2, 2)

        from zope.component.adapter import provideAdapter
        provideAdapter(IDocument, IZopeDublinCore, FauxDCAdapter)

        fc = self._TestView__newView(container)
        info = fc.listContentInfo()[0]

        self.assertEqual(info['id'], 'document')
        self.assertEqual(info['url'], 'document')
        self.assertEqual(info['object'], document)
        self.assertEqual(info['title'], 'faux title')
        self.assertEqual(info['created'], formatTime(FauxDCAdapter.created))
        self.assertEqual(info['modified'], formatTime(FauxDCAdapter.modified))

    def testRemove(self):
        container = self._TestView__newContext()
        subcontainer = self._TestView__newContext()
        container.setObject('subcontainer', subcontainer)
        document = Document()
        container.setObject('document', document)
        document2 = Document()
        container.setObject('document2', document2)

        fc = self._TestView__newView(container)

        self.failIf(getEvents(IObjectModifiedEvent))
        self.failIf(getEvents(IObjectRemovedEvent))

        fc.removeObjects(['document2'])

        self.failUnless(
            getEvents(IObjectRemovedEvent,
                      filter =
                      lambda event:
                      removeAllProxies(event.object) == document2)
           )
        self.failUnless(
            getEvents(IObjectModifiedEvent,
                      filter =
                      lambda event:
                      removeAllProxies(event.object) == container)
           )

        info_list = fc.listContentInfo()

        self.assertEquals(len(info_list), 2)

        ids = map(lambda x: x['id'], info_list)
        self.assert_('subcontainer' in ids)

        objects = map(lambda x: x['object'], info_list)
        self.assert_(subcontainer in objects)

        urls = map(lambda x: x['url'], info_list)
        self.assert_('subcontainer' in urls)

class IDocument(Interface):
    pass

class Document:
    __implements__ = IDocument


class TestCutCopyPaste(PlacefulSetup, TestCase):
    
    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        provideAdapter(IContainer, IZopeContainer, ZopeContainerAdapter)
        provideAdapter(ITraversable, IZopeContainer, ZopeContainerAdapter)
        provideAdapter(None, IObjectCopier, ObjectCopier)
        provideAdapter(None, IObjectMover, ObjectMover)
        provideAdapter(IContainer, IPasteTarget, PasteTarget)
        provideAdapter(IContainer, IMoveSource, MoveSource)
        provideAdapter(IContainer, ICopySource, CopySource)
        provideAdapter(None, IObjectName, ObjectName)
        provideAdapter(IContainer, IPasteNamesChooser, PasteNamesChooser)

        provideAdapter(IAnnotations, IPrincipalClipboard, PrincipalClipboard)
        root_sm = getServiceManager(None)
        svc = PrincipalAnnotationService()
        root_sm.defineService("PrincipalAnnotation", \
            IPrincipalAnnotationService)
        root_sm.provideService("PrincipalAnnotation", svc)

    def testRename(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids=['document1', 'document2']
        for id in ids:
            document = Document()
            container.setObject(id, document)
        fc.renameObjects(ids, ['document1_1', 'document2_2'])
        self.failIf('document1_1' not in container)
        self.failIf('document1' in container)

    def testCopyPaste(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids=['document1', 'document2']
        for id in ids:
            document = Document()
            container.setObject(id, document)
        fc.copyObjects(ids)
        fc.pasteObjects()
        self.failIf('document1' not in container)
        self.failIf('document2' not in container)
        self.failIf('copy_of_document1' not in container)
        self.failIf('copy_of_document2' not in container)

    def testCopyFolder(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids = ['folder1_1']
        fc.copyObjects(ids)
        fc.pasteObjects()
        self.failIf('folder1_1' not in container)
        self.failIf('copy_of_folder1_1' not in container)

    def testCopyFolder2(self):
        container = traverse(self.rootFolder, '/folder1/folder1_1')
        fc = self._TestView__newView(container)
        ids = ['folder1_1_1']
        fc.copyObjects(ids)
        fc.pasteObjects()
        self.failIf('folder1_1_1' not in container)
        self.failIf('copy_of_folder1_1_1' not in container)

    def testCopyFolder3(self):
        container = traverse(self.rootFolder, '/folder1/folder1_1')
        target = traverse(self.rootFolder, '/folder2/folder2_1')
        fc = self._TestView__newView(container)
        tg = self._TestView__newView(target)
        ids = ['folder1_1_1']
        fc.copyObjects(ids)
        tg.pasteObjects()
        self.failIf('folder1_1_1' not in container)
        self.failIf('folder1_1_1' not in target)

    def testCutPaste(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids=['document1', 'document2']
        for id in ids:
            document = Document()
            container.setObject(id, document)
        fc.cutObjects(ids)
        fc.pasteObjects()
        self.failIf('document1' not in container)
        self.failIf('document2' not in container)

    def testCutFolder(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids = ['folder1_1']
        fc.cutObjects(ids)
        fc.pasteObjects()
        self.failIf('folder1_1' not in container)

    def testCutFolder2(self):
        container = traverse(self.rootFolder, '/folder1/folder1_1')
        fc = self._TestView__newView(container)
        ids = ['folder1_1_1']
        fc.cutObjects(ids)
        fc.pasteObjects()
        self.failIf('folder1_1_1' not in container)

    def testCutFolder3(self):
        container = traverse(self.rootFolder, '/folder1/folder1_1')
        target = traverse(self.rootFolder, '/folder2/folder2_1')
        fc = self._TestView__newView(container)
        tg = self._TestView__newView(target)
        ids = ['folder1_1_1']
        fc.cutObjects(ids)
        tg.pasteObjects()
        self.failIf('folder1_1_1' in container)
        self.failIf('folder1_1_1' not in target)

    def _TestView__newView(self, container):
        from zope.app.browser.container.contents import Contents
        from zope.publisher.browser import TestRequest
        return Contents(container, TestRequest())

class Test(BaseTestContentsBrowserView, TestCase):

    def _TestView__newContext(self):
        from zope.app.container.sample import SampleContainer
        from zope.app.content.folder import RootFolder
        from zope.proxy.context import ContextWrapper
        root = RootFolder()
        container = SampleContainer()
        return ContextWrapper(container, root, name='sample')

    def _TestView__newView(self, container):
        from zope.app.browser.container.contents import Contents
        from zope.publisher.browser import TestRequest
        return Contents(container, TestRequest())

def test_suite():
    return TestSuite((
        makeSuite(Test),
        makeSuite(TestCutCopyPaste),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
