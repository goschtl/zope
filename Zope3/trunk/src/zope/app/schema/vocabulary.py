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

$Id: vocabulary.py,v 1.5 2004/03/03 22:54:27 srichter Exp $
"""
from zope.app import zapi
from zope.interface import Interface, implements
from zope.schema.interfaces import IVocabularyRegistry


class IVocabularyFactory(Interface):
    """Can create vocabularies."""

    def __call__(self, context):
        """The context provides a location that the vocabulary can make use
        of."""


class ZopeVocabularyRegistry(object):
    """IVocabularyRegistry that supports global and local utilities."""

    implements(IVocabularyRegistry)
    __slots__ = ()

    def get(self, context, name):
        """See zope.schema.interfaces.IVocabularyRegistry"""
        factory = zapi.getUtility(context, IVocabularyFactory, name)
        return factory(context)
