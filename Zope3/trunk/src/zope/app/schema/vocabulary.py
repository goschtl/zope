##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Implementation of ZCML action to register vocabulary factories.

$Id: vocabulary.py,v 1.4 2003/08/01 21:48:34 srichter Exp $
"""
from zope.interface import implements
from zope.component import getService
from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyRegistry
from zope.testing import cleanup

__metaclass__ = type


class ZopeVocabularyRegistry:
    """IVocabularyRegistry that supports local vocabulary services."""

    implements(IVocabularyRegistry)
    __slots__ = ()

    def get(self, context, name):
        vr = getService(context, "Vocabularies")
        return vr.get(context, name)


def _clear():
    """Re-initialize the vocabulary service."""
    # This should normally only be needed by the testing framework,
    # but is also used for module initialization.
    global vocabularyService
    vocabulary._clear()
    vocabularyService = vocabulary.getVocabularyRegistry()
    vocabulary._clear()
    vocabulary.setVocabularyRegistry(ZopeVocabularyRegistry())


_clear()
cleanup.addCleanUp(_clear)
