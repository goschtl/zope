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

import unittest, doctest

from zope.interface import implements
from zope.app.copypastemove.interfaces import IObjectCopier 
from zope.app.folder import Folder
from zope.app.container.interfaces import INameChooser
from zope.app.exception.interfaces import UserError


class SingleHistory(Folder) :

    implements(INameChooser)
    
    def checkName(self, name, object):
        """Check whether an object name is valid.

        Raise a user error if the name is not valid.
        """
        raise UserError("versions cannot be named by the user.")
        

    def chooseName(self, name, object):
        """Choose a unique valid name for the object

        The given name and object may be taken into account when
        choosing the name.

        """
        return "Version %03d" % (len(self)+1)
        
    
        
         
    
         
class SimpleHistoryStorage(Folder) :
    """
        Implements the probably most simple way of version control in Zope3.
        It uses the following existing Zope mechanisms :
            
           the _p_oid as an identification ticket for objects and their versions
           a Folder as a container for histories were each History is itself a Folder
           
        >>> from policies import VersionableAspectsAdapter
        >>> from zope.app.tests.setup import buildSampleFolderTree
        >>> sample = buildSampleFolderTree()
        >>> histories = SimpleHistoryStorage()
        >>> sample.keys()
        
    """
   

    def getTicket(self, obj) :
        return str(obj._p_oid)
 
    def register(self, obj):
        """ Register an obj for version control.
            Creates a new version history for a resource."""
        history = SingleHistory()
        ticket = self.getTicket(obj)
        self[ticket] = history
        return ticket
        
    def getHistory(self, obj):
        """Internal: return a version history given a version history id."""
        ticket = self.getTicket(obj)
        return self[ticket]
        
  
             
   



def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))
        
        
if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
