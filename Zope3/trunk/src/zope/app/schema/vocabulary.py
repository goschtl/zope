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

"""Implementation of ZCML action to register vocabulary factories."""

from zope.component import getService
from zope.configuration.action import Action
from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyRegistry
from zope.testing import cleanup


def register(_context, name, factory, **kw):
    factory = _context.resolve(factory.strip())
    if kw:
        factory = FactoryKeywordPasser(factory, kw)
    return [
        Action(discriminator=('defineVocabulary', name),
               callable=vocabularyService.register,
               args=(name, factory))
        ]


class FactoryKeywordPasser:
    """Helper that passes additional keywords to the actual factory."""

    def __init__(self, factory, kwargs):
        self.factory = factory
        self.kwargs = kwargs

    def __call__(self, object):
        return self.factory(object, **self.kwargs)


class ZopeVocabularyRegistry(object):
    """IVocabularyRegistry that supports local vocabulary services."""

    __implements__ = IVocabularyRegistry
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
