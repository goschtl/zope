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
from datetime import datetime

from zope.interface import implements
from persistent.dict import PersistentDict
from zope.app.folder import Folder
from zope.app.exception.interfaces import UserError
from zope.app.copypastemove.interfaces import IObjectCopier 
from zope.app.container.interfaces import INameChooser
from zope.app.annotation.interfaces import IAnnotations

from versioning.interfaces import IVersionHistory
from versioning.interfaces import IHistoryStorage
from versioning.interfaces import ICheckoutAware


class VersionHistory(Folder) :
    """ A simple folder implementation where each version
        is labeled '001', '002' etc.
    """
    
    implements(IVersionHistory, INameChooser)
    
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
        return "%03d" % (len(self)+1)
          
      
    
         
class SimpleHistoryStorage(Folder) :
    """
        Implements the probably most simple way of version control in Zope3.
        It uses the following existing Zope mechanisms :
            
           the _p_oid as an identification ticket for objects and their versions
           a Folder as a container for histories were each History is itself a Folder
           
        >>> from versioning.policies import VersionableAspectsAdapter
        >>> from zope.app.tests.setup import buildSampleFolderTree
        >>> sample = buildSampleFolderTree()
        >>> histories = SimpleHistoryStorage()
        >>> sample.keys()
        
    """
    
    implements(IHistoryStorage)
 
    def register(self, obj):
        """ Register an obj for version control.
            Creates a new version history for a resource."""
        history = VersionHistory()      # XXX call IVersionHistory(self) instead?
        ticket = self.getTicket(obj)
        self[ticket] = history
        return ticket
  
    def getTicket(self, obj) :
        """ Returns the persistent oid of an object as
            a ticket that remains stable across time.
        """
        if obj._p_oid is None :
            raise RuntimeError("cannot version uncommited objects")
        return str(obj._p_oid)
  
    def getVersion(self, obj, selector) :
        """ Returns the version of an object that is specified by selector. """
        history = self.getVersionHistory(obj)
        return history[selector]
       
    def getVersionHistory(self, obj):
        """ Returns a version history given a version history id."""
        ticket = self.getTicket(obj)
        return self[ticket]
              
    def getMetadataHistory(self, obj) :
        """ Returns a version history given a version history id."""
        NotImplementedError("metadata support not implemented")
       
    def listVersions(self, obj) :
        """ Returns the versions of an object. The versions are
            returned sorted in the order of appearance. """
        list = self.history.values()
        list.sort()
        return list
        


class DefaultCheckoutAware(object):
    """Default checkout and checkin aware storage extension.
    
    Use this for IHistoryStorage components beeing unable to store checkin
    and checkout information.
    
    XXX Should 'DefaultCheckoutAware' live here?
    
    XXX CAUTION! If currently a checked out object gets deleted
    the counter doesn't get decremented! We should
    
    Asserts IContained (the same object can not live in different
    locations).
    """
    
    implements(ICheckoutAware)
    __used_for__ = IHistoryStorage
    
    namespace_key = 'versioning.interfaces.ICheckoutAware'
    
    def getCheckedOutList(self):
        return self.annotations.get(self.namespace_key)
    
    checkedOutDict = property(getCheckedOutList)
    
    def __init__(self, histories):
        self.histories = histories
        self.annotations = anno = IAnnotations(histories)
        data = self.getCheckedOutList()
        if data is None:
            anno[self.namespace_key] = PersistentDict()
    
    def markAsCheckedOut(self, obj):
        """See versioning.interfaces.ICheckoutAware
        """
        ticket = self.histories.getTicket(obj)
        self.checkedOutDict[ticket] = datetime.now()
        
    def markAsCheckedIn(self, obj):
        """See versioning.interfaces.ICheckoutAware
        """
        ticket = self.histories.getTicket(obj)
        del self.checkedOutDict[ticket]
        
    def isCheckedOut(self, obj):
        """See versioning.interfaces.ICheckoutAware
        """
        ticket = self.histories.getTicket(obj)
        return self.checkedOutDict.has_key(ticket)


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))
        
        
if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
