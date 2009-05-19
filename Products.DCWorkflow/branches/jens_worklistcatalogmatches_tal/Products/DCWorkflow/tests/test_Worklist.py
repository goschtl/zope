##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for the DCWorkflow Worklists module.

$Id$
"""

import unittest

from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.testing import TraversingZCMLLayer
from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFCore.WorkflowTool import WorkflowTool


class WorklistTests(unittest.TestCase):

    layer = TraversingZCMLLayer

    def setUp(self):
        self.site = DummySite('site')
        self.site._path = ''
        self.site._setObject( 'portal_catalog', CatalogTool() )
        self.site.portal_catalog.addIndex('state', 'KeywordIndex')
        self.site._setObject( 'portal_types', DummyTool() )
        self.site._setObject( 'portal_workflow', WorkflowTool() )
        self.site._setObject( 'dummy', DummyContent('dummy') )
        self.site.dummy.state = 'private'
        self.site.portal_catalog.catalog_object(self.site.dummy)
        self._constructDummyWorkflow()

    def _constructDummyWorkflow(self):
        from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

        wftool = self.site.portal_workflow
        wftool._setObject('wf', DCWorkflowDefinition('wf'))
        wftool.setDefaultChain('wf')
        wf = wftool.wf
        wf.worklists.addWorklist('reviewer_queue')

    def _getDummyWorkflow(self):
        wftool = self.site.portal_workflow
        return wftool.wf

    def _getDummyWorklist(self):
        wf = self._getDummyWorkflow()
        return wf.worklists.reviewer_queue

    def test_defaults(self):
        wl = self._getDummyWorklist()
        self.assertEquals(wl.id, 'reviewer_queue')
        self.assertEquals(wl.title, '')
        self.assertEquals(wl.description, '')
        self.assertEquals(wl.var_matches, None)
        self.assertEquals(wl.actbox_name, '')
        self.assertEquals(wl.actbox_url, '')
        self.assertEquals(wl.actbox_icon, '')
        self.assertEquals(wl.actbox_category, 'global')
        self.assertEquals(wl.guard, None)
        self.assertEquals(wl.getAvailableCatalogVars(), ['state'])
        self.assertEquals(wl.getVarMatchKeys(), [])
        self.failIf(wl.search())

    def test_guard_default(self):
        # Without any guard defined, an empty gard is returned
        from AccessControl.SecurityManagement import getSecurityManager
        guard = self._getDummyWorklist().getGuard()
        self.assertEquals(guard.getSummary(), '')
        self.failUnless( guard.check( getSecurityManager()
                                    , self._getDummyWorkflow()
                                    , self.site.dummy
                                    ) )

    def test_catalog_matches_formatted(self):
        # Cataloged variable matches value as formatted string
        wl = self._getDummyWorklist()
        wl.setProperties('', props={'var_match_state': 'public; pending'})
        self.assertEquals(wl.getVarMatchKeys(), ['state'])
        self.assertEquals(wl.getVarMatch('state'), ('public', 'pending'))
        self.assertEquals(wl.getVarMatchText('state'), 'public; pending')
        self.failIf(wl.search())

        wl.setProperties('', props={'var_match_state': 'private'})
        self.assertEquals(wl.getVarMatchKeys(), ['state'])
        self.assertEquals(wl.getVarMatch('state'), ('private',))
        self.assertEquals(wl.getVarMatchText('state'), 'private')
        self.assertEquals(len(wl.search()), 1)

    def test_catalog_matches_tal_python(self):
        # Cataloged variable matches value as formatted string
        wl = self._getDummyWorklist()
        props={'var_match_state': 'python:("public", "pending")'}
        wl.setProperties('', props=props)
        self.assertEquals(wl.getVarMatchKeys(), ['state'])
        self.assertEquals( wl.getVarMatch('state').text
                         , 'python:("public", "pending")'
                         )
        self.assertEquals( wl.getVarMatchText('state')
                         , 'python:("public", "pending")'
                         )
        self.failIf(wl.search())

        props={'var_match_state': 'python:"private"'}
        wl.setProperties('', props=props)
        self.assertEquals(wl.getVarMatchKeys(), ['state'])
        self.assertEquals( wl.getVarMatch('state').text
                         , 'python:"private"'
                         )
        self.assertEquals( wl.getVarMatchText('state')
                         , 'python:"private"'
                         )
        self.assertEquals(len(wl.search()), 1)

    def test_catalog_matches_tal_string(self):
        # Cataloged variable matches value as formatted string
        wl = self._getDummyWorklist()
        props={'var_match_state': 'string:public'}
        wl.setProperties('', props=props)
        self.assertEquals(wl.getVarMatchKeys(), ['state'])
        self.assertEquals( wl.getVarMatch('state').text
                         , 'string:public'
                         )
        self.assertEquals( wl.getVarMatchText('state')
                         , 'string:public'
                         )
        self.failIf(wl.search())

        props={'var_match_state': 'string:private'}
        wl.setProperties('', props=props)
        self.assertEquals(wl.getVarMatchKeys(), ['state'])
        self.assertEquals( wl.getVarMatch('state').text
                         , 'string:private'
                         )
        self.assertEquals( wl.getVarMatchText('state')
                         , 'string:private'
                         )
        self.assertEquals(len(wl.search()), 1)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(WorklistTests),
        ))

if __name__ == '__main__':
    from Products.CMFCore.testing import run
    run(test_suite())
