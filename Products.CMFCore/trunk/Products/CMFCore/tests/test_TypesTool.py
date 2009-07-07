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
""" Unit tests for TypesTool module.

$Id$
"""

import unittest

from Products.CMFCore.testing import FunctionalZCMLLayer
from Products.CMFCore.tests.base.testcase import SecurityTest

class TypesToolTests(SecurityTest):

    layer = FunctionalZCMLLayer

    def _makeOne(self):
        from Products.CMFCore.TypesTool import TypesTool

        return TypesTool()

    def setUp(self):
        from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
        from Products.CMFCore.tests.base.dummy import DummySite
        from Products.CMFCore.tests.base.dummy import DummyUserFolder
        from Products.CMFCore.tests.base.tidata import FTIDATA_DUMMY
        SecurityTest.setUp(self)
        self.site = DummySite('site').__of__(self.root)
        self.acl_users = self.site._setObject( 'acl_users', DummyUserFolder() )
        self.ttool = self.site._setObject( 'portal_types', self._makeOne() )
        fti = FTIDATA_DUMMY[0].copy()
        self.ttool._setObject( 'Dummy Content', FTI(**fti) )
        
        # setup workflow tool
        # to test 'Instance creation conditions' of workflows
        from Products.CMFCore.WorkflowTool import WorkflowTool
        self.site._setObject( 'portal_workflow', WorkflowTool() )
        wftool = self.site.portal_workflow

        from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
        wftool._setObject('wf', DCWorkflowDefinition('wf'))
        wftool.setDefaultChain('wf')
        wf = wftool.wf
        wf.states.addState('initial')
        wf.states.setInitialState('initial')

        from Products.DCWorkflow.Guard import Guard
        g = Guard()
        wf.creation_guard = g
        

    def tearDown(self):
        SecurityTest.tearDown(self)

    def _makeDummyTypeInfo(self):
        from zope.interface import implements
        from Products.CMFCore.interfaces import ITypeInformation

        class ActionTesterTypeInfo:
            implements(ITypeInformation)
            id = 'Dummy Content'

            def listActions(self, info=None, obj=None):
                self._action_info = info
                self._action_obj = obj
                return ()

        return ActionTesterTypeInfo()

    def test_interfaces(self):
        from Products.CMFCore.interfaces import IActionProvider
        from Products.CMFCore.interfaces import ITypesTool
        from Products.CMFCore.TypesTool import TypesTool
        from zope.interface.verify import verifyClass

        verifyClass(IActionProvider, TypesTool)
        verifyClass(ITypesTool, TypesTool)

    def test_listActions(self):
        """test that a full set of context information is passed
           by the types tool
        """
        from Products.CMFCore.tests.base.dummy import DummyContent
        tool = self.ttool
        ti = self._makeDummyTypeInfo()
        setattr( tool, 'Dummy Content', ti )

        dummy = self.site._setObject('dummy', DummyContent('dummy'))
        tool.listActions('fake_info', dummy)

        self.assertEqual(ti._action_info, 'fake_info')
        self.assertEqual(ti._action_obj, dummy)

    def test_allMetaTypes(self):
        """
        Test that everything returned by allMetaTypes can be
        traversed to.
        """
        from Acquisition import aq_base
        from Products.PythonScripts.standard import html_quote
        from webdav.NullResource import NullResource
        tool = self.ttool
        meta_types={}
        # Seems we get NullResource if the method couldn't be traverse to
        # so we check for that. If we've got it, something is b0rked.
        for factype in tool.all_meta_types():
            meta_types[factype['name']]=1
            # The html_quote below is necessary 'cos of the one in
            # main.dtml. Could be removed once that is gone.
            act = tool.unrestrictedTraverse(html_quote(factype['action']))
            self.failIf(type(aq_base(act)) is NullResource)

        # Check the ones we're expecting are there
        self.failUnless(meta_types.has_key('Scriptable Type Information'))
        self.failUnless(meta_types.has_key('Factory-based Type Information'))

    def test_constructContent(self):
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SecurityManager import setSecurityPolicy
        from AccessControl.unauthorized import Unauthorized
        from Products.PythonScripts.PythonScript import PythonScript
        from Products.CMFCore.PortalFolder import PortalFolder
        from Products.CMFCore.TypesTool \
                import ScriptableTypeInformation as STI
        from Products.CMFCore.tests.base.dummy import DummyFactoryDispatcher
        from Products.CMFCore.tests.base.tidata import STI_SCRIPT

        site = self.site
        acl_users = self.acl_users
        ttool = self.ttool
        setSecurityPolicy(self._oldPolicy)
        newSecurityManager(None, acl_users.all_powerful_Oz)
        self.site._owner = (['acl_users'], 'all_powerful_Oz')
        sti_baz = STI('Baz',
                      permission='Add portal content',
                      constructor_path='addBaz')
        ttool._setObject('Baz', sti_baz)
        ttool._setObject( 'addBaz',  PythonScript('addBaz') )
        s = ttool.addBaz
        s.write(STI_SCRIPT)

        f = site._setObject( 'folder', PortalFolder(id='folder') )
        f.manage_addProduct = { 'FooProduct' : DummyFactoryDispatcher(f) }
        f._owner = (['acl_users'], 'user_foo')
        self.assertEqual( f.getOwner(), acl_users.user_foo )

        ttool.constructContent('Dummy Content', container=f, id='page1')
        try:
            ttool.constructContent('Baz', container=f, id='page2')
        except Unauthorized:
            self.fail('CMF Collector issue #165 (Ownership bug): '
                      'Unauthorized raised' )

        wf = site.portal_workflow.wf
        wf.creation_guard.changeFromProperties({'guard_expr':'python:False'})
        try :
            ttool.constructContent('Dummy Content', container=f, id='page3')
        except Unauthorized, e :
            self.assertEqual(str(e), "Cannot create Dummy Content")
        else :
            self.fail("workflow 'Instance creation conditions' does not work")
        
        wf.manager_bypass = 1
        try :
            ttool.constructContent('Dummy Content', container=f, id='page4')
        except Unauthorized:
            self.fail("manager may bypass 'Instance creation conditions'")


class TypeInfoTests:

    def _makeTypesTool(self):
        from Products.CMFCore.TypesTool import TypesTool

        return TypesTool()

    def test_construction( self ):
        ti = self._makeInstance( 'Foo'
                               , description='Description'
                               , meta_type='Foo'
                               , icon='foo.gif'
                               )
        self.assertEqual( ti.getId(), 'Foo' )
        self.assertEqual( ti.Title(), 'Foo' )
        self.assertEqual( ti.Description(), 'Description' )
        self.assertEqual( ti.Metatype(), 'Foo' )
        self.assertEqual( ti.getIcon(), 'foo.gif' )
        self.assertEqual( ti.immediate_view, '' )

        ti = self._makeInstance( 'Foo'
                               , immediate_view='foo_view'
                               )
        self.assertEqual( ti.immediate_view, 'foo_view' )

    def _makeAndSetInstance(self, id, **kw):
        tool = self.tool
        t = self._makeInstance(id, **kw)
        tool._setObject(id,t)
        return tool[id]

    def test_allowType( self ):
        self.tool = self._makeTypesTool()
        ti = self._makeAndSetInstance( 'Foo' )
        self.failIf( ti.allowType( 'Foo' ) )
        self.failIf( ti.allowType( 'Bar' ) )

        ti = self._makeAndSetInstance( 'Foo2', allowed_content_types=( 'Bar', ) )
        self.failUnless( ti.allowType( 'Bar' ) )

        ti = self._makeAndSetInstance( 'Foo3', filter_content_types=0 )
        self.failUnless( ti.allowType( 'Foo3' ) )

    def test_GlobalHide( self ):
        self.tool = self._makeTypesTool()
        tnf = self._makeAndSetInstance( 'Folder', filter_content_types=0)
        taf = self._makeAndSetInstance( 'Allowing Folder'
                                      , allowed_content_types=( 'Hidden'
                                                              ,'Not Hidden'))
        tih = self._makeAndSetInstance( 'Hidden', global_allow=0)
        tnh = self._makeAndSetInstance( 'Not Hidden')
        # make sure we're normally hidden but everything else is visible
        self.failIf     ( tnf.allowType( 'Hidden' ) )
        self.failUnless ( tnf.allowType( 'Not Hidden') )
        # make sure we're available where we should be
        self.failUnless ( taf.allowType( 'Hidden' ) )
        self.failUnless ( taf.allowType( 'Not Hidden') )
        # make sure we're available in a non-content-type-filtered type
        # where we have been explicitly allowed
        taf2 = self._makeAndSetInstance( 'Allowing Folder2'
                                       , allowed_content_types=( 'Hidden'
                                                               , 'Not Hidden'
                                                               )
                                       , filter_content_types=0
                                       )
        self.failUnless ( taf2.allowType( 'Hidden' ) )
        self.failUnless ( taf2.allowType( 'Not Hidden') )

    def test_allowDiscussion( self ):
        ti = self._makeInstance( 'Foo' )
        self.failIf( ti.allowDiscussion() )

        ti = self._makeInstance( 'Foo', allow_discussion=1 )
        self.failUnless( ti.allowDiscussion() )

    def test_listActions( self ):
        from Products.CMFCore.tests.base.tidata import FTIDATA_ACTIONS
        ti = self._makeInstance( 'Foo' )
        self.failIf( ti.listActions() )

        ti = self._makeInstance( **FTIDATA_ACTIONS[0] )
        actions = ti.listActions()
        self.failUnless( actions )

        ids = [ x.getId() for x in actions ]
        self.failUnless( 'view' in ids )
        self.failUnless( 'edit' in ids )
        self.failUnless( 'objectproperties' in ids )
        self.failUnless( 'slot' in ids )

        names = [ x.Title() for x in actions ]
        self.failUnless( 'View' in names )
        self.failUnless( 'Edit' in names )
        self.failUnless( 'Object Properties' in names )
        self.failIf( 'slot' in names )
        self.failUnless( 'Slot' in names )

        visible = [ x.getId() for x in actions if x.getVisibility() ]
        self.failUnless( 'view' in visible )
        self.failUnless( 'edit' in visible )
        self.failUnless( 'objectproperties' in visible )
        self.failIf( 'slot' in visible )

    def test_MethodAliases_methods(self):
        from Products.CMFCore.tests.base.tidata import FTIDATA_CMF15
        ti = self._makeInstance( **FTIDATA_CMF15[0] )
        self.assertEqual( ti.getMethodAliases(), FTIDATA_CMF15[0]['aliases'] )
        self.assertEqual( ti.queryMethodID('view'), 'dummy_view' )
        self.assertEqual( ti.queryMethodID('view.html'), 'dummy_view' )

        ti.setMethodAliases( ti.getMethodAliases() )
        self.assertEqual( ti.getMethodAliases(), FTIDATA_CMF15[0]['aliases'] )

    def test_getInfoData(self):
        ti_data = {'id': 'foo',
                   'title': 'Foo',
                   'description': 'Foo objects are just used for testing.',
                   'content_icon': 'foo_icon.gif',
                   'content_meta_type': 'Foo Content',
                   'factory' : 'cmf.foo',
                   'icon_expr' : 'string:${portal_url}/foo_icon_expr.gif',
                   'add_view_expr': 'string:${folder_url}/foo_add_view',
                   'link_target': '_new'}
        ti = self._makeInstance(**ti_data)
        info_data = ti.getInfoData()
        self.assertEqual(len(info_data), 2)

        self.assertEqual(len(info_data[0]), 10)
        self.assertEqual(info_data[0]['id'], ti_data['id'])
        self.assertEqual(info_data[0]['category'], 'folder/add')
        self.assertEqual(info_data[0]['title'], ti_data['title'])
        self.assertEqual(info_data[0]['description'], ti_data['description'])
        self.assertEqual(info_data[0]['url'].text,
                         'string:${folder_url}/foo_add_view')
        self.assertEqual(info_data[0]['icon'].text,
                         'string:${portal_url}/foo_icon_expr.gif')
        self.assertEqual(info_data[0]['visible'], True)
        self.assertEqual(info_data[0]['available'], ti._checkAvailable)
        self.assertEqual(info_data[0]['allowed'], ti._checkAllowed)
        self.assertEqual(info_data[0]['link_target'], ti.link_target)

        self.assertEqual(set(info_data[1]),
                         set(['url', 'icon', 'available', 'allowed']))

    def test_getInfoData_without_urls(self):
        ti_data = {'id': 'foo',
                   'title': 'Foo',
                   'description': 'Foo objects are just used for testing.',
                   'content_meta_type': 'Foo Content',
                   'factory' : 'cmf.foo'}
        ti = self._makeInstance(**ti_data)
        info_data = ti.getInfoData()
        self.assertEqual(len(info_data), 2)

        self.assertEqual(len(info_data[0]), 10)
        self.assertEqual(info_data[0]['id'], ti_data['id'])
        self.assertEqual(info_data[0]['category'], 'folder/add')
        self.assertEqual(info_data[0]['title'], ti_data['title'])
        self.assertEqual(info_data[0]['description'], ti_data['description'])
        self.assertEqual(info_data[0]['url'], '')
        self.assertEqual(info_data[0]['icon'], '')
        self.assertEqual(info_data[0]['visible'], True)
        self.assertEqual(info_data[0]['available'], ti._checkAvailable)
        self.assertEqual(info_data[0]['allowed'], ti._checkAllowed)
        self.assertEqual(info_data[0]['link_target'], '')

        self.assertEqual(set(info_data[1]), set(['available', 'allowed']))

    def _checkContentTI(self, ti):
        from Products.CMFCore.ActionInformation import ActionInformation
        wanted_aliases = { 'view': 'dummy_view', '(Default)': 'dummy_view' }
        wanted_actions_text0 = 'string:${object_url}/dummy_view'
        wanted_actions_text1 = 'string:${object_url}/dummy_edit_form'
        wanted_actions_text2 = 'string:${object_url}/metadata_edit_form'

        self.failUnless( isinstance( ti._actions[0], ActionInformation ) )
        self.assertEqual( len( ti._actions ), 3 )
        self.assertEqual(ti._aliases, wanted_aliases)
        self.assertEqual(ti._actions[0].action.text, wanted_actions_text0)
        self.assertEqual(ti._actions[1].action.text, wanted_actions_text1)
        self.assertEqual(ti._actions[2].action.text, wanted_actions_text2)

        action0 = ti._actions[0]
        self.assertEqual( action0.getId(), 'view' )
        self.assertEqual( action0.Title(), 'View' )
        self.assertEqual( action0.getActionExpression(), wanted_actions_text0 )
        self.assertEqual( action0.getCondition(), '' )
        self.assertEqual( action0.getPermissions(), ( 'View', ) )
        self.assertEqual( action0.getCategory(), 'object' )
        self.assertEqual( action0.getVisibility(), 1 )

    def _checkFolderTI(self, ti):
        from Products.CMFCore.ActionInformation import ActionInformation
        wanted_aliases = { 'view': '(Default)' }
        wanted_actions_text0 = 'string:${object_url}'
        wanted_actions_text1 = 'string:${object_url}/dummy_edit_form'
        wanted_actions_text2 = 'string:${object_url}/folder_localrole_form'

        self.failUnless( isinstance( ti._actions[0], ActionInformation ) )
        self.assertEqual( len( ti._actions ), 3 )
        self.assertEqual(ti._aliases, wanted_aliases)
        self.assertEqual(ti._actions[0].action.text, wanted_actions_text0)
        self.assertEqual(ti._actions[1].action.text, wanted_actions_text1)
        self.assertEqual(ti._actions[2].action.text, wanted_actions_text2)


class FTIDataTests( TypeInfoTests, unittest.TestCase ):

    def _makeInstance(self, id, **kw):
        from Products.CMFCore.TypesTool import FactoryTypeInformation

        return FactoryTypeInformation(id, **kw)

    def test_interfaces(self):
        from Products.CMFCore.interfaces import ITypeInformation
        from Products.CMFCore.TypesTool import FactoryTypeInformation
        from zope.interface.verify import verifyClass

        verifyClass(ITypeInformation, FactoryTypeInformation)

    def test_properties( self ):
        ti = self._makeInstance( 'Foo' )
        self.assertEqual( ti.product, '' )
        self.assertEqual( ti.factory, '' )

        ti = self._makeInstance( 'Foo'
                               , product='FooProduct'
                               , factory='addFoo'
                               )
        self.assertEqual( ti.product, 'FooProduct' )
        self.assertEqual( ti.factory, 'addFoo' )


class STIDataTests( TypeInfoTests, unittest.TestCase ):

    def _makeInstance(self, id, **kw):
        from Products.CMFCore.TypesTool import ScriptableTypeInformation

        return ScriptableTypeInformation(id, **kw)

    def test_interfaces(self):
        from Products.CMFCore.interfaces import ITypeInformation
        from Products.CMFCore.TypesTool import ScriptableTypeInformation
        from zope.interface.verify import verifyClass

        verifyClass(ITypeInformation, ScriptableTypeInformation)

    def test_properties( self ):
        ti = self._makeInstance( 'Foo' )
        self.assertEqual( ti.permission, '' )
        self.assertEqual( ti.constructor_path, '' )

        ti = self._makeInstance( 'Foo'
                               , permission='Add Foos'
                               , constructor_path='foo_add'
                               )
        self.assertEqual( ti.permission, 'Add Foos' )
        self.assertEqual( ti.constructor_path, 'foo_add' )


class FTIConstructionTestCase:

    def _getTargetClass(self):
        from Products.CMFCore.TypesTool import FactoryTypeInformation

        return FactoryTypeInformation

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_isConstructionAllowed_wo_Container(self):
        self.failIf(self.ti.isConstructionAllowed(None))

    def test_isConstructionAllowed_wo_ProductFactory(self):
        ti = self._makeOne('foo')
        self.failIf(ti.isConstructionAllowed(self.f))

    def test_isConstructionAllowed_wo_Security(self):
        from AccessControl.SecurityManagement import noSecurityManager
        noSecurityManager()
        self.failIf(self.ti.isConstructionAllowed(self.f))

    def test_isConstructionAllowed_for_Omnipotent(self):
        from AccessControl.SecurityManagement import newSecurityManager
        from Products.CMFCore.tests.base.security import OmnipotentUser
        newSecurityManager(None, OmnipotentUser().__of__(self.f))
        self.failUnless(self.ti.isConstructionAllowed(self.f))

    def test_isConstructionAllowed_w_Role(self):
        self.failUnless(self.ti.isConstructionAllowed(self.f))

    def test_isConstructionAllowed_wo_Role(self):
        from AccessControl.SecurityManagement import newSecurityManager
        from Products.CMFCore.tests.base.security import UserWithRoles
        newSecurityManager(None, UserWithRoles('FooViewer').__of__(self.f))
        self.failIf(self.ti.isConstructionAllowed(self.f))

    def test_constructInstance_wo_Roles(self):
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.unauthorized import Unauthorized
        from Products.CMFCore.tests.base.security import UserWithRoles
        newSecurityManager(None, UserWithRoles('FooViewer').__of__(self.f))
        self.assertRaises(Unauthorized,
                          self.ti.constructInstance, self.f, 'foo')

    def test_constructInstance(self):
        self.ti.constructInstance(self.f, 'foo')
        foo = self.f._getOb('foo')
        self.assertEqual(foo.id, 'foo')

    def test_constructInstance_private(self):
        from AccessControl.SecurityManagement import newSecurityManager
        from Products.CMFCore.tests.base.security import UserWithRoles
        newSecurityManager(None, UserWithRoles('NotAFooAdder').__of__(self.f))
        self.ti._constructInstance(self.f, 'foo')
        foo = self.f._getOb('foo')
        self.assertEqual(foo.id, 'foo')

    def test_constructInstance_w_args_kw(self):
        self.ti.constructInstance(self.f, 'bar', 0, 1)
        bar = self.f._getOb('bar')
        self.assertEqual(bar.id, 'bar')
        self.assertEqual(bar._args, (0, 1))

        self.ti.constructInstance(self.f, 'baz', frickle='natz')
        baz = self.f._getOb('baz')
        self.assertEqual(baz.id, 'baz')
        self.assertEqual(baz._kw['frickle'], 'natz')

        self.ti.constructInstance(self.f, 'bam', 0, 1, frickle='natz')
        bam = self.f._getOb('bam')
        self.assertEqual(bam.id, 'bam')
        self.assertEqual(bam._args, (0, 1))
        self.assertEqual(bam._kw['frickle'], 'natz')


class FTIOldstyleConstructionTests(FTIConstructionTestCase, unittest.TestCase):

    def setUp(self):
        from AccessControl.SecurityManagement import newSecurityManager
        from Products.CMFCore.tests.base.dummy import DummyFolder
        from Products.CMFCore.tests.base.security import UserWithRoles
        self.f = DummyFolder(fake_product=1)
        self.ti = self._makeOne('Foo', product='FooProduct', factory='addFoo')
        newSecurityManager(None, UserWithRoles('FooAdder').__of__(self.f))

    def tearDown(self):
        from AccessControl.SecurityManagement import noSecurityManager
        from zope.testing.cleanup import cleanUp
        cleanUp()
        noSecurityManager()

    def test_constructInstance_w_id_munge(self):
        self.f._prefix = 'majyk'
        self.ti.constructInstance(self.f, 'dust')
        majyk_dust = self.f._getOb('majyk_dust')
        self.assertEqual(majyk_dust.id, 'majyk_dust')

    def test_events(self):
        from OFS.interfaces import IObjectWillBeAddedEvent
        from zope.component import adapter
        from zope.component import provideHandler
        from zope.container.interfaces import IContainerModifiedEvent
        from zope.container.interfaces import IObjectAddedEvent
        from zope.lifecycleevent.interfaces import IObjectCreatedEvent
        events = []

        @adapter(IObjectCreatedEvent)
        def _handleObjectCreated(event):
            events.append(event)
        provideHandler(_handleObjectCreated)

        @adapter(IObjectWillBeAddedEvent)
        def _handleObjectWillBeAdded(event):
            events.append(event)
        provideHandler(_handleObjectWillBeAdded)

        @adapter(IObjectAddedEvent)
        def _handleObjectAdded(event):
            events.append(event)
        provideHandler(_handleObjectAdded)

        @adapter(IContainerModifiedEvent)
        def _handleContainerModified(event):
            events.append(event)
        provideHandler(_handleContainerModified)

        self.ti.constructInstance(self.f, 'foo')
        self.assertEquals(len(events), 3)

        evt = events[0]
        self.failUnless(IObjectCreatedEvent.providedBy(evt))
        self.assertEquals(evt.object, self.f.foo)

        evt = events[1]
        self.failUnless(IObjectAddedEvent.providedBy(evt))
        self.assertEquals(evt.object, self.f.foo)
        self.assertEquals(evt.oldParent, None)
        self.assertEquals(evt.oldName, None)
        self.assertEquals(evt.newParent, self.f)
        self.assertEquals(evt.newName, 'foo')

        evt = events[2]
        self.failUnless(IContainerModifiedEvent.providedBy(evt))
        self.assertEquals(evt.object, self.f)


class FTINewstyleConstructionTests(FTIConstructionTestCase, SecurityTest):

    def setUp(self):
        from AccessControl.SecurityManagement import newSecurityManager
        from zope.component import getSiteManager
        from zope.component.interfaces import IFactory
        from Products.CMFCore.tests.base.dummy import DummyFactory
        from Products.CMFCore.tests.base.dummy import DummyFolder
        from Products.CMFCore.tests.base.security import UserWithRoles
        SecurityTest.setUp(self)
        sm = getSiteManager()
        sm.registerUtility(DummyFactory, IFactory, 'test.dummy')

        self.f = DummyFolder()
        self.ti = self._makeOne('Foo', meta_type='Dummy',
                                factory='test.dummy')
        newSecurityManager(None, UserWithRoles('FooAdder').__of__(self.f))

    def tearDown(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()
        SecurityTest.tearDown(self)

    def test_events(self):
        from OFS.interfaces import IObjectWillBeAddedEvent
        from zope.component import adapter
        from zope.component import provideHandler
        from zope.container.interfaces import IContainerModifiedEvent
        from zope.container.interfaces import IObjectAddedEvent
        from zope.lifecycleevent.interfaces import IObjectCreatedEvent
        events = []

        @adapter(IObjectCreatedEvent)
        def _handleObjectCreated(event):
            events.append(event)
        provideHandler(_handleObjectCreated)

        @adapter(IObjectWillBeAddedEvent)
        def _handleObjectWillBeAdded(event):
            events.append(event)
        provideHandler(_handleObjectWillBeAdded)

        @adapter(IObjectAddedEvent)
        def _handleObjectAdded(event):
            events.append(event)
        provideHandler(_handleObjectAdded)

        @adapter(IContainerModifiedEvent)
        def _handleContainerModified(event):
            events.append(event)
        provideHandler(_handleContainerModified)

        self.ti.constructInstance(self.f, 'foo')
        self.assertEquals(len(events), 4)

        evt = events[0]
        self.failUnless(IObjectCreatedEvent.providedBy(evt))
        self.assertEquals(evt.object, self.f.foo)

        evt = events[1]
        self.failUnless(IObjectWillBeAddedEvent.providedBy(evt))
        self.assertEquals(evt.object, self.f.foo)
        self.assertEquals(evt.oldParent, None)
        self.assertEquals(evt.oldName, None)
        self.assertEquals(evt.newParent, self.f)
        self.assertEquals(evt.newName, 'foo')

        evt = events[2]
        self.failUnless(IObjectAddedEvent.providedBy(evt))
        self.assertEquals(evt.object, self.f.foo)
        self.assertEquals(evt.oldParent, None)
        self.assertEquals(evt.oldName, None)
        self.assertEquals(evt.newParent, self.f)
        self.assertEquals(evt.newName, 'foo')

        evt = events[3]
        self.failUnless(IContainerModifiedEvent.providedBy(evt))
        self.assertEquals(evt.object, self.f)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TypesToolTests),
        unittest.makeSuite(FTIDataTests),
        unittest.makeSuite(STIDataTests),
        unittest.makeSuite(FTIOldstyleConstructionTests),
        unittest.makeSuite(FTINewstyleConstructionTests),
        ))

if __name__ == '__main__':
    from Products.CMFCore.testing import run
    run(test_suite())
