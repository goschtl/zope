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
from zope.app.container.interfaces import IContained

from interfaces import IVersionableAspects
  
class VersionableAspectsAdapter(object) :
    """ Implements a simple versioning policy.
        The versionable object is completely copied into the
        object history.
        
        It assumes that the history is of type IContainer
        and the copied object of type IContained.
        
        It further assumes that we only version objects
        that have been persistently stored (and thus have a _p_oid)
        
    """
    
    implements(IVersionableAspects)

    def __init__(self, versionable, histories) :
        """ An adapter for transfering versionable aspects of an object to and from the
            version history of an object.
            
            context must be IVersionable
            histories must be IHistories a storage of multiple object histories
            
            >>> from storage import SimpleHistoryStorage
            >>> from zope.app.tests.setup import buildSampleFolderTree
            >>> sample = buildSampleFolderTree()
            >>> histories = SimpleHistoryStorage()
            >>> a = sample["folder1"]
            >>> b = sample["folder2"]
            >>> histories.register(a)
            >>> histories._histories.values() 
            
            >>> ticket = histories.getTicket(a)
            >>> histories.getHistory(ticket)
            >>> histories.register(b)
            >>> adapter = VersionableAspectsAdapter(a, histories)
            >>> key = adapter.writeAspects()
            
        """

        assert IContained.providedBy(versionable)
      
        self.versionable = versionable
        self.histories = histories
        
    def writeAspects(self) :
        """ 
            Save the versionable aspects of an original object into the object history.
        """   
        history = self.histories.getHistory(self.versionable)
        return IObjectCopier(self.versionable).copyTo(history)        
      
              
    def updateAspects(self, version_specifier) :
        """ Read back the specified versioned aspects from the objects history. """
        history = self.histories.getHistory(self.versionable)
        version = history[version_specifier]
        parent = self.versionable.__parent__
        del parent[self.versionable.__name__]
        IObjectCopier(self.versionable).copyTo(parent)


  



def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))
        
        
if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
           