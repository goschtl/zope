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
A simple repository beeing able to handle linear histories.

"""

import zope.interface
from zope.interface import Interface
from zope.app import zapi

import interfaces

# doc tests import
import unittest
from zope.testing import doctest
from zope.app.tests import ztapi

"""Just here for historical reasons, may be removed later
class DummyHistoryStorage:
    
    def __init__(self):
        self._histories = {}
    
    def getTicket(self, obj):
        return id(obj)
    
    def _getHistory(self, obj):
        return self._histories.setdefault(id(obj), [])
    
    def save(self, obj):
        import copy
        obj_copy = copy.copy(obj)
        self._getHistory(obj).append(obj_copy)
        return self.getTicket(obj_copy)
        
    def load(self, obj, selector):
        return self._histories[id(obj)][selector]
"""

class DummyCheckoutAware(object):
    """Just ignores checkin and checkout without generating exceptions.
    
    Use this for IHistoryStorage components beeing unable to store checkin
    and checkout information.
    """
    
    zope.interface.implements(interfaces.ICheckoutAware)
    __used_for__ = interfaces.IHistoryStorage
    
    def markAsCheckedIn(self, obj):
        """Fake checkin mark doing anything.
        """
        pass
        
    def markAsCheckedOut(self, obj):
        """Fake checkout mark doing anything.
        """
        pass
        
    def isCheckedOut(self, obj):
        """Fake check
        """
        return False

class CopyModifyMergeRepository(object):
    """The repository handles simple linear histories.
    
    x>>> class IPyRefHistoryStorage(Interface):
    x....   pass
    x
    x>>> class DummyHistoryStorage:
    x...    pass
    x
    x>>> ztapi.provideUtility(IPyRefHistoryStorage, DummyHistoryStorage):
    
    XXX VersionableData vermittelt zwischen den Daten und der Storage, was gespeichert werden soll
    >>> ztapi.provideAdapter((IVersionable, IHistoryStorage), IVersionableAspects, VersionableAspects)

    >>> repo = Repository()
    
    >>>
    """

    zope.interface.implements(
        interfaces.ICopyModifyMergeRepository,
        interfaces.IIntrospectableRepository,
    )

    def __init__(self):
        self.histories = zapi.getUtility(IHistoryStorage)
        #self.checkout_blah = zapi.
        
    def applyVersionControl(self, obj):
        """Put the passed object under version control.
        """
        if interfaces.IVersioned.providedBy(obj):
            raise RepositoryError(
                'The resource is already under version control.'
                )
        
        if not interfaces.IVersionable.providedBy(obj):
            raise RepositoryError(
                'This resource cannot be put under version control.'
                )
        
        self._declare_versioned(obj)
        
        # Lets register the object at the IHistoryStorage component
        # 
        # Why register?
        # We like to give the IHistoryStorage component the possibility
        # to veto as early as possible (e.g. to raise "connection to 
        # backend repository lost" or "quota for user Ben exceded" 
        # exceptions or similar)
        self.histories.register(obj)

    def _declare_versioned(obj):
        """Apply bookkeeping needed to recognize an object version controlled.
        """
        ifaces = zope.interface.directlyProvidedBy(obj)
        ifaces += IVersioned
        zope.interface.directlyProvides(object, *ifaces)

    def saveAsVersion(self, obj):
        """Save the current state of the object for later retreival.
        """
        self._saveAsVersion(self, obj)
    
    def _saveAsVersion(self, obj):
        """Save the current state of the object for later retreival.
        """
        versionable_state = zapi.getMultiAdapter(
            (obj, self.histories), IVersionableAspects)
        versionable_state.writeAspect()
    
    def revertToVersion(self, obj, selector):
        """Reverts the object to the selected version.
        
        XXX Do we need to say something about branches?
        """
        versionable_state = zapi.getMultiAdapter(
            (obj, self.histories), IVersionableAspects)
        versionable_state.updateAspects(specifier)
        
    def getVersionHistory(self, obj, selector):
        versionable_state = zapi.getMultiAdapter(
            (obj, self.histories), IVersionableAspects)
        return versionable_state.getApsectsHistory(specifier)
        
    def getMetadataHistory(self, obj):
        versionable_state = zapi.getMultiAdapter(
            (obj, self.histories), IVersionableAspects)
        return versionable_state.getMetadataHistory(specifier)
        

class CheckoutCheckinRepository(CopyModifyMergeRepository):
    """The repository handles simple linear histories.
    """

    zope.interface.implements(
        interfaces.ICheckoutCheckinRepository,
        interfaces.IIntrospectableRepository,
    )

    def saveAsVersion(self, obj):
        # just deimplement ;-) the inherited method as this could
        # confuse the checkout/checkin management
        raise NotImplementedError
    
    def checkin(self, obj):
        """Check in an IVersionable object.
        
        Raises an RepositoryError if the object is not versionable.
        XXX Other exceptions (for repository problems)?
        """
        # the order may be significant for the marking, XXX really?
        checkoutaware = ICheckoutAware(self.histories)
        checkoutaware.markAsCheckedIn(obj)
        self._saveAsVersion(obj)
        
    def checkout(self, obj):
        """Marks the object as checked out (being in use somehow).
        """
        checkoutaware = ICheckoutAware(self.histories)
        checkoutaware.markAsCheckedOut(obj)

    def isCheckedOut(self, obj):
        checkoutaware = ICheckoutAware(self.histories)
        return checkoutaware.isCheckedOut(obj)


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))
if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
