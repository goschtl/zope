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
"""edition package for zope3org"""

import transaction

from zorg.edition.interfaces import IVersionable
from zorg.edition.interfaces import IVersioned
from zorg.edition.interfaces import IHistoryStorage
from zorg.edition.interfaces import ICopyModifyMergeRepository
from zorg.edition.interfaces import RepositoryError

from zope.app import zapi


def registerEdition(object):
    """ Register an object for version control and editions. """
    if IVersionable.providedBy(object):
        history = zapi.queryUtility(IHistoryStorage)
        if history is not None and not IVersioned.providedBy(object):
            rep = ICopyModifyMergeRepository(history)
            rep.applyVersionControl(object)
    else :
        raise RepositoryError(
                'The resource is not versionable.'
                )
                
def saveEdition(object) :
    """ The main function that creates a new edition of an object. """
    if IVersionable.providedBy(object):
        history = zapi.queryUtility(IHistoryStorage)
        if history is not None and not IVersioned.providedBy(object):
            rep = ICopyModifyMergeRepository(history)
            rep.saveAsVersion(object)
    else :
        raise RepositoryError(
                'The resource is not versionable.'
                )
    
