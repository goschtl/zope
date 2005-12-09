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

from zorg.edition.interfaces import IVersionable
from zorg.edition.interfaces import IVersioned
from zorg.edition.interfaces import IHistoryStorage
from zorg.edition.interfaces import ICopyModifyMergeRepository
from zope.app import zapi


def registerVersionControl(event):
    if IVersionable.providedBy(event.object):
        history = zapi.getUtility(IHistoryStorage)
        if history is not None and not IVersioned.providedBy(event.object):
            rep = ICopyModifyMergeRepository(history)
            get_transaction().commit()
            rep.applyVersionControl(event.object)
