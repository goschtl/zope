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


from datetime import datetime
  
import persistent
from BTrees.OOBTree import OOBTree
from BTrees.OIBTree import OIBTree

class TemporalParadox(Exception): pass
  
  
class Version(object) :
    """ Contains a pointer to the versioned data as well
        as some metadata.
    """
   
    implents(IVersion)
    
    def __init__(self, data, metadata) :
        self.data = data
        self.when = datetime.datetime(metadata["time"])
        self.who = metadata["user_name"]
        self.description = metadata["description"]
    
    
class HistoryStorageMixin(object) :

    _histories = None

    def getTicket(self, obj) :
        raise NotImplementedError

    def getHistory(self, obj) :
        """ Returns the history for a versionable object. """  
        ticket = self.getTicket()
        if self.hasHistory(
         
    def load(self, obj, selector) :
        
   
    def save(self, obj) :
    
  
   
      
class SimpleHistoryStorage(Persistent) :
    """ We simply use the ZODB history for our references to
        revisions of an object.
      
    """
    
    def __init__(self) :
        self._histories = OIBTree()
    
    def getTicket(self, obj) :
        return obj._p_oid
            
    
        
        
# 
# 
# class HystoryJar(object) :
#     """A ZODB Connection-like object that provides access to data
#     but prevents history from being changed.
#     
#     Shamelessly copied from Zope2 OFS.History and thus ported to Zope3
#   
#     XXX is there something in Zope3 that already corresponds to this.
#     """
# 
#     def __init__(self, base):
#         self.__base__=base
# 
#     def __getattr__(self, name):
#         return getattr(self.__base__, name)
# 
#     def commit(self, object, transaction):
#         if object._p_changed:
#             raise TemporalParadox, "You can't change history!"
# 
#     def abort(*args, **kw): pass
# 
#     tpc_begin = tpc_finish = abort
#     
#          
#     def _getVersionFromHistory(self, ticket, revision):
#         """ Retrieves a revision from a history of an object. """
#         
#         serial=revision['serial']
#         state=ticket._p_jar.oldstate(self, serial)
#         rev=ticket.__class__.__basicnew__()
#         rev._p_jar=HystoryJar(ticket._p_jar)
#         rev._p_oid=ticket._p_oid
#         rev._p_serial=serial
#         rev.__setstate__(state)
#         rev._p_changed=0
#        
#         return IVersion(rev, revision)
#         
#     def getVersions(obj):
#         """Get a list of versions."""
#         revisions = obj._p_jar.db().history(self._p_oid, None, 20)
#         if revisions is None:
#             return ()
#         return [self._getVersionFromHistory(r) for r in revisions]
#         



def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))
        
        
if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
