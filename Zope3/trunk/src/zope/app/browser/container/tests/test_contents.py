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
$Id: test_contents.py,v 1.25 2003/09/21 17:30:29 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.adapter import provideAdapter

from zope.app.interfaces.container import IContainer
from zope.app.interfaces.copypastemove import IObjectMover

from zope.app.traversing import traverse
from zope.app.interfaces.copypastemove import IObjectMover
from zope.app.interfaces.copypastemove import IObjectCopier

from zope.app.copypastemove import ObjectMover
from zope.app.copypastemove import ObjectCopier

from zope.app.event.tests.placelesssetup import getEvents, clearEvents
from zope.app.interfaces.event import IObjectModifiedEvent
from zope.app.interfaces.container import IObjectRemovedEvent
from zope.interface import Interface, implements
from zope.proxy import removeAllProxies

from zope.app.interfaces.copypastemove import IPrincipalClipboard
from zope.app.copypastemove import PrincipalClipboard
from zope.component import getServiceManager
from zope.app.services.principalannotation import PrincipalAnnotationService
from zope.app.interfaces.services.principalannotation \
    import IPrincipalAnnotationService
from zope.app.interfaces.annotation import IAnnotations
from zope.app.container.contained import contained

class BaseTestContentsBrowserView(PlacefulSetup):
    """Base class for testing browser contents.

    Subclasses need to define a method, '_TestView__newContext', that
    takes no arguments and that returns a new empty test view context.

    Subclasses need to define a method, '_TestView__newView', that
    takes a context object and that returns a new test view.
    """

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        provideAdapter(None, IObjectCopier, ObjectCopier)
        provideAdapter(None, IObjectMover, ObjectMover)

        provideAdapter(IAnnotations, IPrincipalClipboard, PrincipalClipboard)
        root_sm = getServiceManager(None)
        svc = PrincipalAnnotationService()
        root_sm.defineService("PrincipalAnnotation", \
            IPrincipalAnnotationService)
        root_sm.provideService("PrincipalAnnotation", svc)

    def testInfo(self):
        # Do we get the correct information back from ContainerContents?
        container = self._TestView__newContext()
        subcontainer = self._TestView__newContext()
        container['subcontainer'] = subcontainer
        document = Document()
        container['document'] = document

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
        container['document'] = document

        from datetime import datetime
        from zope.app.interfaces.dublincore import IZopeDublinCore
        class FauxDCAdapter:
            implements(IZopeDublinCore)

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
        self.assertEqual(info['created'], '1/1/01 1:01 AM ')
        self.assertEqual(info['modified'], '2/2/02 2:02 AM ')

    def testRemove(self):
        container = self._TestView__newContext()
        subcontainer = self._TestView__newContext()
        container['subcontainer'] = subcontainer
        document = Document()
        container['document'] = document
        document2 = Document()
        container['document2'] = document2

        fc = self._TestView__newView(container)

        fc.request.form.update({'ids': ['document2']})

        fc.removeObjects()

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
    implements(IDocument)


class Principal:

    def getId(self):
        return 'bob'


class TestCutCopyPaste(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        provideAdapter(None, IObjectCopier, ObjectCopier)
        provideAdapter(None, IObjectMover, ObjectMover)

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
            container[id] = document
        fc.request.form.update({'rename_ids': ids,
                                'new_value': ['document1_1', 'document2_2']
                                })
        fc.renameObjects()
        self.failIf('document1_1' not in container)
        self.failIf('document1' in container)

    def testCopyPaste(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids=['document1', 'document2']
        for id in ids:
            document = Document()
            container[id] = document

        fc.request.form['ids'] = ids
        fc.copyObjects()
        fc.pasteObjects()
        self.failIf('document1' not in container)
        self.failIf('document2' not in container)
        self.failIf('document1-2' not in container)
        self.failIf('document2-2' not in container)

    def testCopyFolder(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids = ['folder1_1']
        fc.request.form['ids'] = ids
        fc.copyObjects()
        fc.pasteObjects()
        self.failIf('folder1_1' not in container)
        self.failIf('folder1_1-2' not in container)

    def testCopyFolder2(self):
        container = traverse(self.rootFolder, '/folder1/folder1_1')
        fc = self._TestView__newView(container)
        ids = ['folder1_1_1']
        fc.request.form['ids'] = ids
        fc.copyObjects()
        fc.pasteObjects()
        self.failIf('folder1_1_1' not in container)
        self.failIf('folder1_1_1-2' not in container)

    def testCopyFolder3(self):
        container = traverse(self.rootFolder, '/folder1/folder1_1')
        target = traverse(self.rootFolder, '/folder2/folder2_1')
        fc = self._TestView__newView(container)
        tg = self._TestView__newView(target)
        ids = ['folder1_1_1']
        fc.request.form['ids'] = ids
        fc.copyObjects()
        tg.pasteObjects()
        self.failIf('folder1_1_1' not in container)
        self.failIf('folder1_1_1' not in target)

    def testCutPaste(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids=['document1', 'document2']
        for id in ids:
            document = Document()
            container[id] = document
        fc.request.form['ids'] = ids
        fc.cutObjects()
        fc.pasteObjects()
        self.failIf('document1' not in container)
        self.failIf('document2' not in container)

    def testCutFolder(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids = ['folder1_1']
        fc.request.form['ids'] = ids
        fc.cutObjects()
        fc.pasteObjects()
        self.failIf('folder1_1' not in container)

    def testCutFolder2(self):
        container = traverse(self.rootFolder, '/folder1/folder1_1')
        fc = self._TestView__newView(container)
        ids = ['folder1_1_1']
        fc.request.form['ids'] = ids
        fc.cutObjects()
        fc.pasteObjects()
        self.failIf('folder1_1_1' not in container)

    def testCutFolder3(self):
        container = traverse(self.rootFolder, '/folder1/folder1_1')
        target = traverse(self.rootFolder, '/folder2/folder2_1')
        fc = self._TestView__newView(container)
        tg = self._TestView__newView(target)
        ids = ['folder1_1_1']
        fc.request.form['ids'] = ids
        fc.cutObjects()
        tg.pasteObjects()
        self.failIf('folder1_1_1' in container)
        self.failIf('folder1_1_1' not in target)

    def _TestView__newView(self, container):
        from zope.app.browser.container.contents import Contents
        from zope.publisher.browser import TestRequest
        request = TestRequest()
        request.setUser(Principal())
        return Contents(container, request)

class Test(BaseTestContentsBrowserView, TestCase):

    def _TestView__newContext(self):
        from zope.app.container.sample import SampleContainer
        from zope.app.content.folder import rootFolder
        root = rootFolder()
        container = SampleContainer()
        return contained(container, root, 'sample')

    def _TestView__newView(self, container):
        from zope.app.browser.container.contents import Contents
        from zope.publisher.browser import TestRequest
        request = TestRequest()
        request.setUser(Principal())
        return Contents(container, request)

def test_suite():
    return TestSuite((
        makeSuite(Test),
        makeSuite(TestCutCopyPaste),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
