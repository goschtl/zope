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

from zope.app import zapi
from zope.app.folder import Folder
from zope.app.annotation.interfaces import IAnnotatable
from zope.app.exception.interfaces import UserError
from zope.app.copypastemove.interfaces import IObjectCopier 
from zope.app.container.interfaces import INameChooser
from zope.app.annotation.interfaces import IAnnotations
from zope.app.uniqueid.interfaces import IUniqueIdUtility
from zope.app.servicenames import Authentication

from versioning.interfaces import IVersionHistory
from versioning.interfaces import IHistoryStorage
from versioning.interfaces import IVersion
from versioning.interfaces import ICheckoutAware


class VersionPrincipalNotFound(Exception):
    pass
    


class VersionHistory(Folder) :
    """ A simple folder implementation where each version
        is labeled '001', '002' etc.
    """
    
    implements(IVersionHistory, INameChooser)
    
    def checkName(self, name, obj):
        """Check whether an object name is valid.

        Raise a user error if the name is not valid.
        """
        raise UserError("versions cannot be named by the user.")
        

    def chooseName(self, name, obj):
        """Choose a unique valid name for the object

        The given name and object may be taken into account when
        choosing the name.

        """
        return "%03d" % (len(self)+1)
          
    # del verbieten
    
    def __setitem__(self, key, obj):
        """
        """
        info = IVersion(obj)
        super(VersionHistory, self).__setitem__(key, info)
         
         
         
class SimpleHistoryStorage(Folder) :
    """
        Implements the probably most simple way of version control in Zope3.
        It uses the following existing Zope mechanisms :
            
           a unique id as an identification ticket for objects and their versions
           a Folder as a container for histories were each History is itself a Folder
           
        >>> from versioning.policies import VersionableAspectsAdapter
        >>> from zope.app.tests.setup import buildSampleFolderTree
        >>> sample = buildSampleFolderTree()
        >>> histories = SimpleHistoryStorage()
        >>> sample.keys()
        
    """
    
    implements(IHistoryStorage, IAnnotatable)
    
    def __init__(self) :
        super(SimpleHistoryStorage, self).__init__()
        #self.unique_ids = zapi.getUtility(IUniqueIdUtility)
        
 
    def register(self, obj):
        """ Register an obj for version control.
            Creates a new version history for a resource."""
        history = VersionHistory()      # XXX call IVersionHistory(self) instead?
        ticket = self.getTicket(obj)
        self[ticket] = history
        return ticket
  
    def getTicket(self, obj) :
        """ Returns a unique id of an object as
            a ticket that remains stable across time.
        """
        if obj._p_oid is None :
            raise RuntimeError("cannot version uncommited object")
        return unicode(obj._p_oid, "iso-8859-1")
        
        # XXX unique id utility is broken
        return str(self.unique_ids.register(obj))
    
  
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
        history = list(self.getVersionHistory(obj).values())
        history.sort(lambda l,r:cmp(l.__name__, r.__name__))
        return history


class Version(object) :
    """An adapter for versionable data. 
    """
    
    implements(IVersion)
    
    __parent__ = __name__ = None
    
    def __init__(self, obj):
        self.obj = obj
        self.time = datetime.now()
    
    def getData(self):
        return self.obj
        
    def getTimestamp(self):
        return self.time
    
    def getLabel(self):
        return self.__name__
    
    def getName(self):
        return 'Version %d' % int(self.getLabel())
        
        
    def getComment(self):
        return 'no comment'
    
    def getPrincipal(self):
        """ Returns the id of the principal that is versioning the data. """  
        auth = zapi.getService(Authentication)
        for principal in auth.getPrincipals('') :
            return principal.getLogin()
        return VersionPrincipalNotFound
 
    
    data = property(getData)
    timestamp = property(getTimestamp)
    label = property(getLabel)
    name = property(getName)
    
    comment = property(getComment)
    principal = property(getPrincipal)



class DefaultCheckoutAware(object):
    """Default checkout and checkin aware storage extension.
    
    Restrictions:
    
        Asserts IContained (the same object can not live in different
        locations). If currently a checked out object gets deleted
        the counter doesn't get decremented! 
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
