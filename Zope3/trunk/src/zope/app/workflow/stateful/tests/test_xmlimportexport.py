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
import unittest
from StringIO import StringIO

from zope.interface.verify import verifyClass
from zope.interface.implements import implements

from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.component.adapter import provideAdapter
from zope.component import getAdapter

from zope.security.checker import CheckerPublic

from zope.app.dublincore.annotatableadapter \
     import ZDCAnnotatableAdapter
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.annotation \
     import IAnnotatable, IAnnotations, IAttributeAnnotatable

from zope.app.interfaces.services.configuration \
     import IUseConfigurable

from zope.app.workflow.stateful.definition \
     import StatefulProcessDefinition, State, Transition

from zope.app.interfaces.workflow import IProcessDefinitionImportHandler
from zope.app.interfaces.workflow import IProcessDefinitionExportHandler
from zope.app.workflow.stateful.xmlimportexport \
     import XMLImportHandler, XMLExportHandler




xml_text = """<?xml version="1.0"?>
<workflow type="StatefulWorkflow" title="TestPD">

  <schema name="Some.path.to.an.ISchemaClass">
  </schema>

  <states>
    <state title="State2" name="state2"/>
    <state title="State1" name="state1"/>
    <state title="initial" name="INITIAL"/>
  </states>

  <transitions>
     
      <transition sourceState="state2"
                  destinationState="INITIAL"
                  script="some.path.to.some.script"
                  permission="zope.View"
                  triggerMode="Manual"
                  title="State2toINITIAL"
                  name="state2_initial"/>
    
     
      <transition sourceState="INITIAL"
                  destinationState="state1"
                  permission="zope.Public"
                  triggerMode="Automatic"
                  title="INITIALtoState1"
                  name="initial_state1"/>
    
     
      <transition sourceState="state1"
                  destinationState="state2"
                  condition="python: 1==1"
                  permission="zope.Public"
                  triggerMode="Manual"
                  title="State1toState2"
                  name="state1_state2"/>
    
  </transitions>
  
</workflow>
"""


class TestProcessDefinition(StatefulProcessDefinition):
    __implements__ = IAttributeAnnotatable, IUseConfigurable, \
                     StatefulProcessDefinition.__implements__

# need to patch this cause these classes are used directly
# in the import/export classes
implements(State, IAttributeAnnotatable)
implements(Transition, IAttributeAnnotatable)



class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        provideAdapter(IAttributeAnnotatable, IAnnotations, AttributeAnnotations)
        provideAdapter(IAnnotatable, IZopeDublinCore, ZDCAnnotatableAdapter)

    def testInterface(self):
        verifyClass(IProcessDefinitionImportHandler, XMLImportHandler)
        verifyClass(IProcessDefinitionExportHandler, XMLExportHandler)

    def testImport(self):
        testpd = TestProcessDefinition()
        handler = XMLImportHandler()
        
        self.assertEqual(handler.canImport(testpd, StringIO(xml_text)), True)
        self.assertEqual(handler.canImport(None, StringIO(xml_text)), False)
        self.assertEqual(handler.canImport(None, StringIO('<some><nonworking/><xml/></some>')), False)

        handler.doImport(testpd, StringIO(xml_text))

        self.assertEqual(testpd.getRelevantDataSchema(), 'Some.path.to.an.ISchemaClass')
        self.assertEqual(getAdapter(testpd, IZopeDublinCore).title, 'TestPD')
        
        self.assertEqual(len(testpd.states), 3)
        self.assertEqual(len(testpd.transitions), 3)

        st = testpd.states['INITIAL']
        self.assert_(isinstance(st, State))
        self.assertEqual(getAdapter(st, IZopeDublinCore).title, 'initial')
                           
        st = testpd.states['state1']
        self.assert_(isinstance(st, State))
        self.assertEqual(getAdapter(st, IZopeDublinCore).title, 'State1')

        st = testpd.states['state2']
        self.assert_(isinstance(st, State))
        self.assertEqual(getAdapter(st, IZopeDublinCore).title, 'State2')


        tr = testpd.transitions['initial_state1']
        self.assert_(isinstance(tr, Transition))
        self.assertEqual(getAdapter(tr, IZopeDublinCore).title, 'INITIALtoState1')
        self.assertEqual(tr.sourceState, 'INITIAL')
        self.assertEqual(tr.destinationState, 'state1')
        self.assertEqual(tr.condition, None)
        self.assertEqual(tr.script, None)
        self.assertEqual(tr.permission, CheckerPublic)
        self.assertEqual(tr.triggerMode, 'Automatic')
        
        tr = testpd.transitions['state1_state2']
        self.assert_(isinstance(tr, Transition))
        self.assertEqual(getAdapter(tr, IZopeDublinCore).title, 'State1toState2')
        self.assertEqual(tr.sourceState, 'state1')
        self.assertEqual(tr.destinationState, 'state2')
        self.assertEqual(tr.condition, 'python: 1==1')
        self.assertEqual(tr.script, None)
        self.assertEqual(tr.permission, CheckerPublic)
        self.assertEqual(tr.triggerMode, 'Manual')
        
        tr = testpd.transitions['state2_initial']
        self.assert_(isinstance(tr, Transition))
        self.assertEqual(getAdapter(tr, IZopeDublinCore).title, 'State2toINITIAL')
        self.assertEqual(tr.sourceState, 'state2')
        self.assertEqual(tr.destinationState, 'INITIAL')
        self.assertEqual(tr.condition, None)
        self.assertEqual(tr.script, 'some.path.to.some.script')
        self.assertEqual(tr.permission, 'zope.View')
        self.assertEqual(tr.triggerMode, 'Manual')

    def testExport(self):
        # XXX TBD before Merge into HEAD !!!!
        pass
        

        

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
