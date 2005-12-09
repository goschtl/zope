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
from zope.app.traversing.interfaces import IContainmentRoot

from interfaces import IVersionableAspects
  
class VersionableAspectsAdapter(object) :
    """ Implements a simple versioning policy.
        The versionable object is completely copied into the
        object history.
        
        It assumes that the history is of type IContainer
        and the copied object of type IContained.
        
        It further assumes that we only version objects
        that have been persistently stored and thus are
        able to be adapted to zope.app.keyreference.interfaces.IKeyReference.
        
    """
    
    implements(IVersionableAspects)

    def __init__(self, versionable, histories) :
        """ An adapter for transfering versionable aspects of an object to and from the
            version history of an object.
          
            >>> from storage import SimpleHistoryStorage
            >>> from zope.app.testing.setup import buildSampleFolderTree
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
        
    def writeAspects(self, message=None) :
        """ 
            Save the versionable aspects of an original object into 
            the object history.
        """
        # XXX we currently throw away the message
        history = self.histories.getVersionHistory(self.versionable)
        return IObjectCopier(self.versionable).copyTo(history)        
      
    def updateAspects(self, version_specifier) :
        """ 
            Read back the specified versioned aspects from the 
            objects history.
        """
        
        history = self.histories.getVersionHistory(self.versionable)
        version = history[version_specifier]
        self.copyVersionedData(version, self.versionable)
              
    def copyVersionedData(self, source, target) :
        """ The internal copy routine """
        parent = target.__parent__
        name = target.__name__
        
        # arrggghh!
        # when the target lives in the zodb root for now we raise an 
        # exception. We have to think about what reverting to the root
        # means first.
        db_root = target._p_jar.root()
        root_names = db_root.keys()
        for key, obj in db_root.items():
            if obj is target:
                raise RuntimeError, "Can not copy versioned state to root."
        else:
            del parent[name]
            IObjectCopier(source.data).copyTo(parent, name)


class ReplaceWithCopyPolicy(VersionableAspectsAdapter) :
    """ 
        A specific policy that updates the original
        by a replacement with a copy of versioned data.
        As long as the user has only access via traversal
        paths this policy requires that external python 
        references are updated if needed.
    """
    
    def copyVersionedData(self, source, target) :
        """ Replaces the original with a copied version. """
         
        parent = target.__parent__
        name = target.__name__       
        del parent[name]
        IObjectCopier(source.data).copyTo(parent, name)
 
 
class UpdateStatusPolicy(VersionableAspectsAdapter) :
    """ Implements a more complex policy that leaves Python
        references of the original content objects intact.
        
        It also assumes that we only version objects
        that have been persistently stored (and thus have a _p_oid)
        
    """
    
    def copyVersionedData(self, source, target) :
        """ Copies the state of source to target. """
        for key, value in source.data.__getstate__().items() :
            if key not in ('__name__', '__parent__') :
                setattr(target, key, value)

       

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))
        
        
if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
           