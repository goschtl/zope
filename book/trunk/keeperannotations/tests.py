##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Unit tests for KeeperAnnotations

$Id$
"""
import unittest

from zope.interface import classImplements
from zope.testing.doctestunit import DocTestSuite

from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.folder import Folder
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.app.annotation.interfaces import \
     IAnnotations, IAnnotatable, IAttributeAnnotatable
from zope.app.dublincore.interfaces import IWriteZopeDublinCore
from zope.app.location.interfaces import ILocation
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.location.traversing import LocationPhysicallyLocatable
from zope.app.tests import ztapi
from zope.app.tests.placelesssetup import setUp, tearDown 

from book.keeperannotations.interfaces import IKeeperAnnotatable 
from book.keeperannotations import KeeperAnnotations 
  
def customSetUp():
    setUp()
    classImplements(Folder, IAttributeAnnotatable)
    ztapi.provideAdapter(IKeeperAnnotatable, IAnnotations,
                         KeeperAnnotations)
    ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                         LocationPhysicallyLocatable)
    ztapi.provideAdapter(IAnnotatable, IWriteZopeDublinCore,
                         ZDCAnnotatableAdapter)
    ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                         AttributeAnnotations)
  
def test_suite():
    return unittest.TestSuite((
        DocTestSuite('book.keeperannotations', 
                     setUp=customSetUp, tearDown=tearDown),
        ))
  
if __name__ == '__main__':
      unittest.main(defaultTest='test_suite')
