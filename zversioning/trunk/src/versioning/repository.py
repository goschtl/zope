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

from versioning import interfaces

# doc tests imports
import unittest
from zope.testing import doctest
from zope.app.tests import ztapi


class CopyModifyMergeRepository(object):
    """The repository handles simple linear histories.
    """

    zope.interface.implements(
        interfaces.ICopyModifyMergeRepository,
        interfaces.IIntrospectableRepository,
    )

    def __init__(self, histories):
        self.histories = histories
        
    def applyVersionControl(self, obj, metadata=None):
        """Put the passed object under version control.
        """
        if interfaces.IVersioned.providedBy(obj):
            raise interfaces.RepositoryError(
                'The resource is already under version control.'
                )
        
        if not interfaces.IVersionable.providedBy(obj):
            raise interfaces.RepositoryError(
                'This resource cannot be put under version control.'
                )
        
        self._declare_versioned(obj)
        
        # Lets register the object at the IHistoryStorage component
        # 
        # Why register?
        # We like to give the IHistoryStorage component the possibility
        # to do inevitable things or veto as early as possible (e.g. to 
        # raise "connection to backend repository lost" or "quota for 
        # user John exceded" exceptions or similar)
        self.histories.register(obj)
        
        # save initial version
        versionable_state = zapi.getMultiAdapter(
            (obj, self.histories), interfaces.IVersionableAspects)
        versionable_state.writeAspects(metadata)

    def _declare_versioned(self, obj):
        """Apply bookkeeping needed to recognize an object version controlled.
        """
        ifaces = zope.interface.directlyProvidedBy(obj)
        ifaces += interfaces.IVersioned
        zope.interface.directlyProvides(obj, *ifaces)

    def saveAsVersion(self, obj, metadata=None):
        """Save the current state of the object for later retreival.
        """
        self._saveAsVersion(self, obj)
    
    def _saveAsVersion(self, obj, metadata=None):
        """Save the current state of the object for later retreival.
        """
        versionable_state = zapi.getMultiAdapter(
            (obj, self.histories), interfaces.IVersionableAspects)
        versionable_state.writeAspects(metadata)
    
    def revertToVersion(self, obj, selector):
        """Reverts the object to the selected version.
        
        XXX Do we need to say something about branches?
        """
        versionable_state = zapi.getMultiAdapter(
            (obj, self.histories), interfaces.IVersionableAspects)
        versionable_state.updateAspects(specifier)
        
    def getTicket(self, obj):
        return self.histories.getTicket(obj)
        
    def getVersion(self, obj, selector):
        return self.histories.getVersion(obj, selector)
        
    def listVersions(self, obj):
        return self.histories.listVersions(obj)
        

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
    
    def checkin(self, obj, metadata=None):
        """Check in an IVersionable object.
        
        Raises an RepositoryError if the object is not versionable.
        XXX Other exceptions (for repository problems)?
        """
        # the order may be significant for the marking, XXX really?
        checkoutaware = interfaces.ICheckoutAware(self.histories)
        checkoutaware.markAsCheckedIn(obj)
        self._saveAsVersion(obj)
        
    def checkout(self, obj):
        """Marks the object as checked out (being in use somehow).
        """
        checkoutaware = interfaces.ICheckoutAware(self.histories)
        checkoutaware.markAsCheckedOut(obj)

    def isCheckedOut(self, obj):
        checkoutaware = interfaces.ICheckoutAware(self.histories)
        return checkoutaware.isCheckedOut(obj)


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))
if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
