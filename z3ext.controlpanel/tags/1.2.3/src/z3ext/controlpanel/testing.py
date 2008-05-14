##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" setup z3ext.controlpanel

$Id$
"""
import os
from zope import component
from zope.app.testing import setup
from zope.annotation.attribute import AttributeAnnotations
from zope.app.component.hooks import getSite, setSite
from zope.app.testing.functional import ZCMLLayer

from z3ext.controlpanel import storage, root, interfaces


def setUpControlPanel():
    setup.setUpTraversal()
    setup.setUpSiteManagerLookup()

    component.provideAdapter(root.getSettings, name='settings')
    component.provideAdapter(AttributeAnnotations)
    component.provideUtility(storage.DataStorage())
    component.provideUtility(root.RootConfiglet(), interfaces.IConfiglet)


z3extControlPanelLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'z3extControlPanelLayer', allow_teardown=True)
