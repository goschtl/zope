##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""
This file contains some tests of zope.app.versioncontrol to figure
out whether the existing implementation fits our needs.


"""
import unittest
from zope.interface import implements
from zope.app.container.sample import SampleContainer
from zope.app.tests import placelesssetup
from zope.app.tests import ztapi

# import basic test infrastructure from existing version control implementation
from zope.app.versioncontrol.tests import setUp, tearDown, name

from zope.testing import doctest


import persistent
import zope.interface
import zope.app.annotation.attribute
import zope.app.annotation.interfaces
import zope.app.traversing.interfaces
import zope.app.versioncontrol.repository
import zope.interface.verify

from zope.app.versioncontrol import interfaces
from zope.app.tests import ztapi
from zope.app.tests.setup import setUpTraversal
from zope.interface import classImplements

from zope.app.traversing.interfaces import ITraversable, ITraverser
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.location.traversing import LocationPhysicallyLocatable
from zope.app.traversing.adapters import RootPhysicallyLocatable
from zope.app.traversing.adapters import Traverser

from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.app.annotation.interfaces import IAnnotatable, IAnnotations
from zope.app.container.interfaces import IContainer
from zope.app.file.interfaces import IFile
from zope.app.file.file import File
from zope.app.folder.folder import Folder

from zope.app.copypastemove.interfaces import IObjectCopier
from zope.app.copypastemove import ObjectCopier

from zope.app.container.interfaces import IWriteContainer, INameChooser
from zope.app.container.contained import NameChooser


def setUp(test) :
    """ Sets up a test and registers some commonly used adapters. """
    
    placelesssetup.setUp()
    setUpTraversal()
 
    classImplements(File, IAttributeAnnotatable)
    classImplements(Folder, IAttributeAnnotatable)

    ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations, AttributeAnnotations)
    ztapi.provideAdapter(None, ITraverser, Traverser)
    ztapi.provideAdapter(None, ITraversable, DefaultTraversable)
    ztapi.provideAdapter(None, IPhysicallyLocatable, LocationPhysicallyLocatable)
    ztapi.provideAdapter(IContainmentRoot, IPhysicallyLocatable, RootPhysicallyLocatable)
    ztapi.provideAdapter(IAnnotatable, IZopeDublinCore, ZDCAnnotatableAdapter)

    # for copy and moves
    ztapi.provideAdapter(None, IObjectCopier, ObjectCopier)
    ztapi.provideAdapter(IWriteContainer, INameChooser, NameChooser)

 
def tearDown(test) :
    placelesssetup.tearDown()

   
    
def buildDatabaseRoot():
    """Opens a connection to a test database and returns the root object
    """
     
    # Now we need to create a database with an instance of our sample object 
    # to work with:
    
    from ZODB.tests import util
    db = util.DB()
    connection = db.open()
    return connection.root()

def buildRepository(factory=zope.app.versioncontrol.repository.Repository, interaction=True):
    """Setup a zope.app.versioncontrol repository
    
    Placing an object under version control requires an instance of an
    `IVersionControl` object.  This package provides an implementation of 
    this interface on the `Repository` class (from
    `zope.app.versioncontrol.repository`).  Only the `IVersionControl` 
    instance is responsible for providing version control operations; 
    an instance should never be asked to perform operations directly.
    """
    
    repository = factory()
    assert zope.interface.verify.verifyObject(
               interfaces.IVersionControl,
               repository)
               
    if interaction :

        # In order to actually use version control, there must be an
        # interaction.  This is needed to allow the framework to determine the
        # user making changes.  Let's set up an interaction now. First we need a
        # principal. For our purposes, a principal just needs to have an id:
        class FauxPrincipal:
           def __init__(self, id):
               self.id = id
        principal = FauxPrincipal('bob')
    
        # Then we need to define an participation for the principal in the
        # interaction:
        class FauxParticipation:
            interaction=None
            def __init__(self, principal):
                self.principal = principal
        participation = FauxParticipation(principal)
    
        # Finally, we can create the interaction:
        import zope.security.management
        zope.security.management.newInteraction(participation)

    return repository


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        doctest.DocFileSuite("../README.txt", setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite("../MOTIVATION.txt", setUp=setUp, tearDown=tearDown),
        ))
if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
